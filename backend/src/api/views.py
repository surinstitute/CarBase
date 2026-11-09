from django.db.models import Count, Max, Min, Prefetch
from django.http import Http404
from django.utils.text import slugify
from django_countries import countries
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.serializers import (
    BaseModelDetailSerializer,
    BaseModelSerializer,
    BatteryPackSerializer,
    CommercialModelDetailSerializer,
    CommercialModelSerializer,
    EMotorSerializer,
    EngineSerializer,
    FuelTankSerializer,
    GroupSerializer,
    MakeSerializer,
    ModelGenerationDetailSerializer,
    ModelGenerationSerializer,
    PlatformSerializer,
    PowerTrainSerializer,
    RecallSerializer,
    TransmissionSerializer,
    VehicleSerializer,
)
from catalog.filters import (
    POWERTRAIN_TYPE_ARCHITECTURES,
    BaseModelFilter,
    CommercialModelFilter,
    RecallFilter,
    VehicleFilter,
)
from catalog.models import (
    BaseModel,
    BatteryPack,
    CommercialModel,
    EMotor,
    Engine,
    FuelTank,
    Group,
    Make,
    ModelGeneration,
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
            "model__model_generation__platform",
            "powertrain",
            "transmissionId",
            "climate_package_assignment__climate_package",
            "model__model_generation__commercial_model__make",
            "safety_package_assignment__safety_package",
            "charging_package_assignment__charging_package",
        )
        .prefetch_related(
            "powertrain__engine_fitments__engine",
            "powertrain__motor_fitments__e_motor",
            "powertrain__battery_fitments__battery_pack",
            "powertrain__fuel_fitments__fuel_tank",
            Prefetch(
                "model__image_placements",
                queryset=ModelImagePlacement.objects.filter(
                    is_visible=True
                ).select_related("image"),
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
        .order_by(
            "-model__year",
            "model__model_generation__commercial_model__make__name",
            "model__model_generation__commercial_model__name",
            "variant_name",
            "id",
        )
    )


def _vehicle_summary_queryset():
    return (
        Vehicle.objects.select_related(
            "model",
            "model__model_generation__platform",
            "model__model_generation__commercial_model__make",
            "powertrain",
            "transmissionId",
        )
        .prefetch_related(
            "powertrain__engine_fitments__engine",
            "powertrain__motor_fitments__e_motor",
            "powertrain__battery_fitments__battery_pack",
            "powertrain__fuel_fitments__fuel_tank",
        )
        .order_by("variant_name", "id")
    )


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.annotate(
        make_count=Count("makes", distinct=True),
        model_year_count=Count("makes__commercial_models__generations__model_years", distinct=True),
        vehicle_count=Count(
            "makes__commercial_models__generations__model_years__model_vehicles",
            distinct=True,
        ),
    ).order_by("name")
    serializer_class = GroupSerializer


class MakeViewSet(ReadOnlyModelViewSet):
    queryset = (
        Make.objects.select_related("group")
        .annotate(
            model_generation_count=Count("commercial_models__generations", distinct=True),
            model_year_count=Count("commercial_models__generations__model_years", distinct=True),
            vehicle_count=Count(
                "commercial_models__generations__model_years__model_vehicles", distinct=True
            ),
        )
        .order_by("name")
    )
    serializer_class = MakeSerializer


class CommercialModelViewSet(ReadOnlyModelViewSet):
    queryset = (
        CommercialModel.objects.select_related("make")
        .annotate(
            generation_count=Count("generations", distinct=True),
            start_year=Min("generations__model_years__year"),
            end_year=Max("generations__model_years__year"),
        )
        .order_by("make__name", "name", "id")
    )
    serializer_class = CommercialModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommercialModelFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            generations = (
                ModelGeneration.objects.select_related("commercial_model__make", "platform")
                .annotate(start_year=Min("model_years__year"), end_year=Max("model_years__year"))
                .order_by("generation_prefix", "generation_number", "id")
            )
            queryset = queryset.prefetch_related(Prefetch("generations", queryset=generations))
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CommercialModelDetailSerializer
        return super().get_serializer_class()


def _base_model_queryset():
    return (
        BaseModel.objects.select_related(
            "model_generation__commercial_model__make", "model_generation__platform"
        )
        .order_by(
            "model_generation__commercial_model__make__name",
            "model_generation__commercial_model__name",
            "model_generation__generation_prefix",
            "model_generation__generation_number",
            "year",
            "body_style",
        )
        .prefetch_related(
            Prefetch(
                "image_placements",
                queryset=ModelImagePlacement.objects.filter(is_visible=True).select_related(
                    "image"
                ),
                to_attr="visible_image_placements",
            )
        )
    )


def _catalog_vehicles_prefetch():
    return Prefetch(
        "model_vehicles",
        queryset=Vehicle.objects.select_related("powertrain"),
        to_attr="catalog_vehicles",
    )


class ModelGenerationViewSet(ReadOnlyModelViewSet):
    queryset = (
        ModelGeneration.objects.select_related("commercial_model__make", "platform")
        .annotate(
            start_year=Min("model_years__year"),
            end_year=Max("model_years__year"),
        )
        .order_by("commercial_model__make__name", "commercial_model__name", "generation_prefix", "generation_number")
    )
    serializer_class = ModelGenerationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            models = _base_model_queryset().prefetch_related(_catalog_vehicles_prefetch())
            queryset = queryset.prefetch_related(Prefetch("model_years", queryset=models))
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ModelGenerationDetailSerializer
        return super().get_serializer_class()


class BaseModelViewSet(ReadOnlyModelViewSet):
    serializer_class = BaseModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseModelFilter

    def get_queryset(self):
        queryset = _base_model_queryset()
        if self.action == "list":
            queryset = queryset.prefetch_related(_catalog_vehicles_prefetch())
        if self.action in ("retrieve", "by_path"):
            queryset = queryset.select_related("warranty")
            queryset = queryset.prefetch_related(
                "safety_ratings",
                Prefetch("model_vehicles", queryset=_vehicle_summary_queryset()),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BaseModelDetailSerializer
        return BaseModelSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path=(
            r"by-path/(?P<make_slug>[^/.]+)/(?P<model_slug>[^/.]+)/"
            r"(?P<generation_slug>[^/.]+)/(?P<model_year>[^/.]+)"
        ),
    )
    def by_path(self, request, make_slug, model_slug, generation_slug, model_year):
        try:
            year_text, body_style = model_year.split("-", maxsplit=1)
            year = int(year_text)
        except ValueError as error:
            raise Http404("Invalid model-year path.") from error

        candidates = self.get_queryset().filter(
            model_generation__commercial_model__make__slug=make_slug,
            year=year,
        )
        for base_model in candidates:
            generation = base_model.model_generation
            if (
                slugify(generation.commercial_model.name) == model_slug
                and slugify(generation.generation or "gen") == generation_slug
                and (
                    base_model.body_style == body_style
                    or (body_style == "unspecified" and not base_model.body_style)
                )
            ):
                return Response(
                    BaseModelDetailSerializer(
                        base_model, context={"request": request}
                    ).data
                )

        raise Http404("Model-year not found.")

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        queryset = BaseModelFilter(
            request.query_params, queryset=BaseModel.objects.all()
        ).qs
        model_name = request.query_params.get("model", "").strip()

        model_names = (
            queryset.order_by("model_generation__commercial_model__name")
            .values_list("model_generation__commercial_model__name", flat=True)
            .distinct()
        )

        if model_name:
            queryset = queryset.filter(model_generation__commercial_model__name__iexact=model_name)

        years = queryset.order_by("-year").values_list("year", flat=True).distinct()
        body_styles = (
            queryset.exclude(body_style__isnull=True)
            .exclude(body_style="")
            .order_by("body_style")
            .values_list("body_style", flat=True)
            .distinct()
        )
        country_codes = (
            queryset.exclude(model_vehicles__assembly_country__isnull=True)
            .exclude(model_vehicles__assembly_country="")
            .values_list("model_vehicles__assembly_country", flat=True)
            .distinct()
        )
        assembly_countries = sorted(
            ({"code": code, "name": countries.name(code)} for code in country_codes),
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
    queryset = PowerTrain.objects.select_related("make").all().order_by("name")
    serializer_class = PowerTrainSerializer


class TransmissionViewSet(ReadOnlyModelViewSet):
    queryset = Transmission.objects.select_related("maker").all().order_by("name")
    serializer_class = TransmissionSerializer


class VehicleViewSet(ReadOnlyModelViewSet):
    queryset = _vehicle_queryset()
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = VehicleFilter

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        queryset = VehicleFilter(
            request.query_params, queryset=Vehicle.objects.all()
        ).qs
        years = (
            queryset.order_by("-model__year")
            .values_list("model__year", flat=True)
            .distinct()
        )
        country_codes = (
            queryset.exclude(assembly_country__isnull=True)
            .exclude(assembly_country="")
            .order_by("assembly_country")
            .values_list("assembly_country", flat=True)
            .distinct()
        )
        powertrain_types = [
            name
            for name, architectures in POWERTRAIN_TYPE_ARCHITECTURES.items()
            if queryset.filter(powertrain__architecture__in=architectures).exists()
        ]
        make_ids = queryset.values_list(
            "model__model_generation__commercial_model__make_id", flat=True
        ).distinct()
        group_ids = (
            queryset.values_list("model__model_generation__commercial_model__make__group_id", flat=True)
            .exclude(model__model_generation__commercial_model__make__group_id__isnull=True)
            .distinct()
        )
        makes = Make.objects.filter(makeId__in=make_ids).order_by("name")
        groups = Group.objects.filter(groupId__in=group_ids).order_by("name")
        return Response(
            {
                "years": list(years),
                "powertrainTypes": powertrain_types,
                "assemblyCountries": [
                    {"code": code, "name": countries.name(code)}
                    for code in country_codes
                ],
                "makes": [
                    {"id": str(make.makeId), "name": make.name} for make in makes
                ],
                "groups": [
                    {"id": str(group.groupId), "name": group.name} for group in groups
                ],
            }
        )


class RecallViewSet(ReadOnlyModelViewSet):
    queryset = (
        Recall.objects.select_related("maker")
        .prefetch_related("affected_models")
        .order_by("-published_date", "id")
    )
    serializer_class = RecallSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecallFilter
