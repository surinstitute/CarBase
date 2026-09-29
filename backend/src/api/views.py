from django_filters.rest_framework import DjangoFilterBackend
from django_countries import countries
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.serializers import (
    BaseModelSerializer,
    BatteryPackSerializer,
    EMotorSerializer,
    EngineSerializer,
    FuelTankSerializer,
    GroupSerializer,
    MakeSerializer,
    PlatformSerializer,
    PowerTrainSerializer,
    TransmissionSerializer,
    VehicleSerializer,
)
from catalog.models import (
    BaseModel,
    BatteryPack,
    EMotor,
    Engine,
    FuelTank,
    Group,
    Make,
    Platform,
    PowerTrain,
    Transmission,
    Vehicle,
)
from catalog.filters import BaseModelFilter, VehicleFilter


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer


class MakeViewSet(ReadOnlyModelViewSet):
    queryset = Make.objects.select_related("group").all().order_by("name")
    serializer_class = MakeSerializer


class BaseModelViewSet(ReadOnlyModelViewSet):
    queryset = (
        BaseModel.objects.select_related("make", "platform")
        .prefetch_related("safety_ratings")
        .all()
        .order_by("make__name", "model")
    )
    serializer_class = BaseModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseModelFilter

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        queryset = BaseModel.objects.all()
        make_id = request.query_params.get("make", "").strip()
        model_name = request.query_params.get("model", "").strip()
        assembly_country = request.query_params.get("assembly_country", "").strip()

        if make_id:
            queryset = queryset.filter(make_id=make_id)

        if assembly_country:
            queryset = queryset.filter(
                model_vehicles__assembly_country__iexact=assembly_country
            )

        model_names = queryset.order_by("model").values_list("model", flat=True).distinct()

        if model_name:
            queryset = queryset.filter(model__iexact=model_name)

        years = queryset.order_by("-year").values_list("year", flat=True).distinct()
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
    queryset = (
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
        .all()
    )
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VehicleFilter
