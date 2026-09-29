from django.db.models import Prefetch
from django_countries import countries
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.serializers import (
    BaseModelDetailSerializer,
    BaseModelSerializer,
    BatteryPackSerializer,
    EMotorSerializer,
    EngineSerializer,
    FuelTankSerializer,
    GroupSerializer,
    MakeSerializer,
    PlatformSerializer,
    PowerTrainSerializer,
    RecallSerializer,
    TransmissionSerializer,
    VehicleSerializer,
)
from catalog.filters import (
    POWERTRAIN_TYPE_ARCHITECTURES,
    BaseModelFilter,
    RecallFilter,
    VehicleFilter,
)
from catalog.models import (
    BaseModel,
    BatteryPack,
    EMotor,
    Engine,
    FuelTank,
    Group,
    Make,
    ModelImagePlacement,
    Platform,
    PowerTrain,
    Recall,
    Transmission,
    Vehicle,
)


def _vehicle_queryset():
    return (
        Vehicle.objects.select_related(
            "model",
            "model__platform",
            "powertrain",
            "transmissionId",
            "model__make",
            "safety_package",
            "charging_package",
        )
        .prefetch_related(
            "powertrain__engine_fitments__engine",
            "powertrain__motor_fitments__e_motor",
            "powertrain__battery_fitments__battery_pack",
            "powertrain__fuel_fitments__fuel_tank",
            Prefetch(
                "model__image_placements",
                queryset=ModelImagePlacement.objects.filter(is_visible=True)
                .select_related("image")
                .order_by("sort_order", "id"),
                to_attr="visible_image_placements",
            ),
            "charging_ports",
            "charge_time_results",
            "regulatory_approvals__source_docs",
            "compliance_records",
            "efficiency_results",
            "range_results",
            "emissions_results",
            "acceleration_results",
            "top_speed_results",
            "monthly_sales",
            "model__recalls",
        )
        .order_by("model__make__name", "model__model", "variant_name", "id")
    )


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer


class MakeViewSet(ReadOnlyModelViewSet):
    queryset = Make.objects.select_related("group").all().order_by("name")
    serializer_class = MakeSerializer


class BaseModelViewSet(ReadOnlyModelViewSet):
    serializer_class = BaseModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseModelFilter

    def get_queryset(self):
        queryset = BaseModel.objects.select_related("make", "platform").order_by(
            "make__name", "model"
        ).prefetch_related(
            Prefetch(
                "image_placements",
                queryset=ModelImagePlacement.objects.filter(is_visible=True)
                .select_related("image")
                .order_by("sort_order", "id"),
                to_attr="visible_image_placements",
            )
        )
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "safety_ratings",
                Prefetch("model_vehicles", queryset=_vehicle_queryset()),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BaseModelDetailSerializer
        return BaseModelSerializer

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        queryset = BaseModelFilter(request.query_params, queryset=BaseModel.objects.all()).qs
        model_name = request.query_params.get("model", "").strip()

        model_names = queryset.order_by("model").values_list("model", flat=True).distinct()

        if model_name:
            queryset = queryset.filter(model__iexact=model_name)

        years = queryset.order_by("-year").values_list("year", flat=True).distinct()
        body_styles = queryset.exclude(body_style__isnull=True).exclude(
            body_style=""
        ).order_by("body_style").values_list("body_style", flat=True).distinct()
        country_codes = (
            queryset.exclude(model_vehicles__assembly_country__isnull=True)
            .exclude(model_vehicles__assembly_country="")
            .values_list("model_vehicles__assembly_country", flat=True)
            .distinct()
        )
        assembly_countries = sorted(
            (
                {"code": code, "name": countries.name(code)}
                for code in country_codes
            ),
            key=lambda country: country["name"],
        )
        return Response(
            {
                "models": list(model_names),
                "years": list(years),
                "bodyStyles": list(body_styles),
                "powertrainTypes": list(POWERTRAIN_TYPE_ARCHITECTURES),
                "assemblyCountries": assembly_countries,
            }
        )


class PlatformViewSet(ReadOnlyModelViewSet):
    queryset = Platform.objects.all().order_by("name")
    serializer_class = PlatformSerializer


class EngineViewSet(ReadOnlyModelViewSet):
    queryset = Engine.objects.select_related("maker").all().order_by("name")
    serializer_class = EngineSerializer


class BatteryPackViewSet(ReadOnlyModelViewSet):
    queryset = BatteryPack.objects.select_related("group").all().order_by("name")
    serializer_class = BatteryPackSerializer


class FuelTankViewSet(ReadOnlyModelViewSet):
    queryset = FuelTank.objects.select_related("maker").all().order_by("name")
    serializer_class = FuelTankSerializer


class EMotorViewSet(ReadOnlyModelViewSet):
    queryset = EMotor.objects.select_related("maker").all().order_by("name")
    serializer_class = EMotorSerializer


class PowerTrainViewSet(ReadOnlyModelViewSet):
    queryset = PowerTrain.objects.select_related("make").all().order_by(
        "name"
    )
    serializer_class = PowerTrainSerializer


class TransmissionViewSet(ReadOnlyModelViewSet):
    queryset = Transmission.objects.select_related("maker").all().order_by("name")
    serializer_class = TransmissionSerializer


class VehicleViewSet(ReadOnlyModelViewSet):
    queryset = _vehicle_queryset()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VehicleFilter

class RecallViewSet(ReadOnlyModelViewSet):
    queryset = Recall.objects.select_related("maker").prefetch_related(
        "affected_models"
    ).order_by("-published_date", "id")
    serializer_class = RecallSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecallFilter
