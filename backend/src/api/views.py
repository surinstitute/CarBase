from django.db.models import Max, Min, Prefetch, Q
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
    ModelGeneration,
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
            "model__model_generation__make",
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
                .select_related("image"),
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
            "model__model_generation__make__name",
            "model__model_generation__model",
            "variant_name",
            "id",
        )
    )


class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer


class MakeViewSet(ReadOnlyModelViewSet):
    queryset = Make.objects.select_related("group").all().order_by("name")
    serializer_class = MakeSerializer


class ModelGenerationViewSet(ReadOnlyModelViewSet):
    queryset = ModelGeneration.objects.select_related("make", "platform").annotate(
        start_year=Min("model_years__year"),
        end_year=Max("model_years__year"),
    ).order_by("make__name", "model", "generation_prefix", "generation_number")
    serializer_class = ModelGenerationSerializer

    @action(detail=False, methods=["get"], url_path="cards")
    def cards(self, request):
        filtered_models = BaseModelFilter(
            request.query_params,
            queryset=BaseModel.objects.select_related("model_generation__make"),
        ).qs
        model_groups = (
            filtered_models.values(
                "model_generation__make_id",
                "model_generation__make__name",
                "model_generation__make__slug",
                "model_generation__model",
            )
            .annotate(start_year=Min("year"), end_year=Max("year"))
            .order_by("model_generation__make__name", "model_generation__model")
        )
        page_groups = self.paginate_queryset(model_groups)
        groups = page_groups if page_groups is not None else list(model_groups)

        group_filter = Q(pk__in=[])
        for group in groups:
            group_filter |= Q(
                model_generation__make_id=group["model_generation__make_id"],
                model_generation__model=group["model_generation__model"],
            )

        models_by_group = {}
        page_models = (
            filtered_models.filter(group_filter)
            .select_related("model_generation__make")
            .order_by(
                "model_generation__make__name",
                "model_generation__model",
                "model_generation__generation_prefix",
                "model_generation__generation_number",
                "year",
                "body_style",
            )
        )
        for model in page_models:
            key = (str(model.model_generation.make_id), model.model_generation.model)
            generations = models_by_group.setdefault(key, {})
            generations.setdefault(
                str(model.model_generation_id),
                {
                    "label": model.model_generation.generation or "Gen",
                    "modelId": str(model.pk),
                    "prefix": model.model_generation.generation_prefix or "Gen",
                    "number": model.model_generation.generation_number,
                },
            )

        cards = []
        for group in groups:
            key = (
                str(group["model_generation__make_id"]),
                group["model_generation__model"],
            )
            generations = sorted(
                models_by_group.get(key, {}).values(),
                key=lambda generation: (
                    generation["prefix"],
                    generation["number"] is None,
                    generation["number"] or 0,
                ),
            )
            cards.append(
                {
                    "id": f"{key[0]}:{key[1]}",
                    "makeId": key[0],
                    "makeName": group["model_generation__make__name"],
                    "makeSlug": group["model_generation__make__slug"],
                    "modelName": key[1],
                    "startYear": group["start_year"],
                    "endYear": group["end_year"],
                    "generations": [
                        {"label": generation["label"], "modelId": generation["modelId"]}
                        for generation in generations
                    ],
                }
            )

        body_styles = list(
            filtered_models.exclude(body_style__isnull=True)
            .exclude(body_style="")
            .order_by("body_style")
            .values_list("body_style", flat=True)
            .distinct()
        )
        response = {
            "count": self.paginator.page.paginator.count
            if page_groups is not None
            else len(cards),
            "next": self.paginator.get_next_link() if page_groups is not None else None,
            "previous": self.paginator.get_previous_link()
            if page_groups is not None
            else None,
            "filterOptions": {
                "makes": [
                    {
                        "id": str(make["makeId"]),
                        "name": make["name"],
                        "slug": make["slug"],
                    }
                    for make in Make.objects.order_by("name").values(
                        "makeId", "name", "slug"
                    )
                ],
                "bodyStyles": body_styles,
            },
            "results": cards,
        }
        return Response(response)


class BaseModelViewSet(ReadOnlyModelViewSet):
    serializer_class = BaseModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BaseModelFilter

    def get_queryset(self):
        queryset = BaseModel.objects.select_related(
            "model_generation__make", "model_generation__platform"
        ).order_by(
            "model_generation__make__name",
            "model_generation__model",
            "model_generation__generation_prefix",
            "model_generation__generation_number",
            "year",
            "body_style",
        ).prefetch_related(
            Prefetch(
                "image_placements",
                queryset=ModelImagePlacement.objects.filter(is_visible=True)
                .select_related("image"),
                to_attr="visible_image_placements",
            )
        )
        if self.action == "retrieve":
            queryset = queryset.select_related("warranty")
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
        queryset = BaseModelFilter(
            request.query_params, queryset=BaseModel.objects.all()
        ).qs
        model_name = request.query_params.get("model", "").strip()

        model_names = queryset.order_by("model_generation__model").values_list(
            "model_generation__model", flat=True
        ).distinct()

        if model_name:
            queryset = queryset.filter(model_generation__model__iexact=model_name)

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

    @action(detail=False, methods=["get"], url_path="filter-options")
    def filter_options(self, request):
        queryset = VehicleFilter(request.query_params, queryset=Vehicle.objects.all()).qs
        years = queryset.order_by("-model__year").values_list(
            "model__year", flat=True
        ).distinct()
        countries = (
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
            "model__model_generation__make_id", flat=True
        ).distinct()
        group_ids = queryset.values_list(
            "model__model_generation__make__group_id", flat=True
        ).exclude(model__model_generation__make__group_id__isnull=True).distinct()
        makes = Make.objects.filter(makeId__in=make_ids).order_by("name")
        groups = Group.objects.filter(groupId__in=group_ids).order_by("name")
        return Response(
            {
                "years": list(years),
                "powertrainTypes": powertrain_types,
                "assemblyCountries": [
                    {"code": code, "name": countries.name(code)}
                    for code in countries
                ],
                "makes": [
                    {"id": str(make.makeId), "name": make.name} for make in makes
                ],
                "groups": [
                    {"id": str(group.groupId), "name": group.name}
                    for group in groups
                ],
            }
        )

class RecallViewSet(ReadOnlyModelViewSet):
    queryset = Recall.objects.select_related("maker").prefetch_related(
        "affected_models"
    ).order_by("-published_date", "id")
    serializer_class = RecallSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecallFilter
