import django_filters
from django.db.models import Case, F, IntegerField, Q, Value, When
from paradedb.functions import Score
from paradedb.search import ParadeDB, PhrasePrefix

from .models import BaseModel, ModelGeneration, Recall, Vehicle
from .types import BodyStyle, PowerTrainArchitecture


POWERTRAIN_TYPE_ARCHITECTURES = {
    "combustion": (PowerTrainArchitecture.ICE,),
    "hybrid": (
        PowerTrainArchitecture.MILD_HYBRID,
        PowerTrainArchitecture.SERIES_HYBRID,
        PowerTrainArchitecture.PARALLEL_HYBRID,
        PowerTrainArchitecture.POWER_SPLIT_HYBRID,
        PowerTrainArchitecture.PHEV,
    ),
    "plug_in_hybrid": (PowerTrainArchitecture.PHEV,),
    "electric": (
        PowerTrainArchitecture.BEV,
        PowerTrainArchitecture.FCEV,
    ),
}


class BaseModelFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    q = django_filters.CharFilter(method="filter_search")
    make = django_filters.UUIDFilter(field_name="model_generation__make_id")
    model = django_filters.CharFilter(
        field_name="model_generation__model", lookup_expr="iexact"
    )
    year = django_filters.NumberFilter(field_name="year")
    body_style = django_filters.ChoiceFilter(
        field_name="body_style", choices=BodyStyle.choices
    )
    powertrain_type = django_filters.ChoiceFilter(
        choices=[(value, value) for value in POWERTRAIN_TYPE_ARCHITECTURES],
        method="filter_powertrain_type",
    )
    assembly_country = django_filters.CharFilter(
        field_name="model_vehicles__assembly_country",
        lookup_expr="iexact",
        distinct=True,
    )

    class Meta:
        model = BaseModel
        fields = [
            "search",
            "q",
            "make",
            "model",
            "year",
            "body_style",
            "powertrain_type",
            "assembly_country",
        ]

    def filter_search(self, queryset, _name, value):
        normalized_value = (value or "").strip()
        if not normalized_value:
            return queryset
        search_query = ParadeDB(
            PhrasePrefix(normalized_value.lower())
        )
        matching_generations = list(
            ModelGeneration.objects.filter(
                Q(model=search_query) | Q(generation_prefix=search_query)
            )
            .annotate(score=Score())
            .order_by("-score")
            .values_list("pk", flat=True)
        )
        if not matching_generations:
            return queryset.none()
        ordering = Case(
            *[
                When(model_generation_id=pk, then=Value(index))
                for index, pk in enumerate(matching_generations)
            ],
            output_field=IntegerField(),
        )
        return queryset.filter(model_generation_id__in=matching_generations).annotate(
            search_rank=ordering
        ).order_by("search_rank")

    def filter_powertrain_type(self, queryset, _name, value):
        architectures = POWERTRAIN_TYPE_ARCHITECTURES.get(value)
        if architectures is None:
            return queryset
        return queryset.filter(
            model_vehicles__powertrain__architecture__in=architectures
        ).distinct()


class VehicleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    q = django_filters.CharFilter(method="filter_search")
    model = django_filters.UUIDFilter(field_name="model_id")
    make = django_filters.UUIDFilter(field_name="model__model_generation__make_id")
    group = django_filters.UUIDFilter(
        field_name="model__model_generation__make__group_id"
    )
    year = django_filters.NumberFilter(field_name="model__year")
    powertrain_type = django_filters.ChoiceFilter(
        choices=[(value, value) for value in POWERTRAIN_TYPE_ARCHITECTURES],
        method="filter_powertrain_type",
    )
    assembly_country = django_filters.CharFilter(
        field_name="assembly_country", lookup_expr="iexact"
    )
    safety = django_filters.BooleanFilter(method="filter_safety")
    sort = django_filters.ChoiceFilter(
        choices=(
            ("newest", "Newest"),
            ("az", "A-Z"),
            ("price_asc", "Price ascending"),
            ("price_desc", "Price descending"),
        ),
        method="filter_sort",
    )
    powertrain = django_filters.UUIDFilter(field_name="powertrain_id")
    transmission = django_filters.UUIDFilter(field_name="transmissionId_id")
    variant_name = django_filters.CharFilter(
        field_name="variant_name", lookup_expr="iexact"
    )

    class Meta:
        model = Vehicle
        fields = [
            "search",
            "q",
            "model",
            "make",
            "group",
            "year",
            "powertrain_type",
            "assembly_country",
            "safety",
            "sort",
            "powertrain",
            "transmission",
            "variant_name",
        ]

    def filter_search(self, queryset, _name, value):
        normalized_value = (value or "").strip()
        if not normalized_value:
            return queryset
        search_query = ParadeDB(
            PhrasePrefix(normalized_value.lower())
        )
        matching_generation_ids = ModelGeneration.objects.filter(
            Q(model=search_query) | Q(generation_prefix=search_query)
        ).values_list("pk", flat=True)
        matching_model_ids = list(
            BaseModel.objects.filter(
                model_generation_id__in=matching_generation_ids
            ).values_list("pk", flat=True)
        )
        return (
            queryset.filter(
                Q(variant_name=search_query) | Q(model_id__in=matching_model_ids)
            )
            .annotate(score=Score())
            .order_by("-score")
        )

    def filter_powertrain_type(self, queryset, _name, value):
        architectures = POWERTRAIN_TYPE_ARCHITECTURES.get(value)
        if architectures is None:
            return queryset
        return queryset.filter(powertrain__architecture__in=architectures)

    def filter_safety(self, queryset, _name, value):
        return queryset.filter(safety_package_assignment__isnull=not value)

    def filter_sort(self, queryset, _name, value):
        if value == "az":
            return queryset.order_by(
                "model__model_generation__make__name",
                "model__model_generation__model",
                "variant_name",
                "id",
            )
        if value == "price_asc":
            return queryset.order_by(
                F("price_amount").asc(nulls_last=True),
                "model__model_generation__make__name",
                "model__model_generation__model",
                "id",
            )
        if value == "price_desc":
            return queryset.order_by(
                F("price_amount").desc(nulls_last=True),
                "model__model_generation__make__name",
                "model__model_generation__model",
                "id",
            )
        return queryset.order_by(
            "-model__year",
            "model__model_generation__make__name",
            "model__model_generation__model",
            "variant_name",
            "id",
        )

class RecallFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Recall
        fields = ["q"]

    def filter_search(self, queryset, _name, value):
        normalized_value = (value or "").strip()
        if not normalized_value:
            return queryset
        return queryset.filter(
            Q(recall_number__icontains=normalized_value)
            | Q(title__icontains=normalized_value)
            | Q(maker__name__icontains=normalized_value)
            | Q(
                affected_models__model_generation__model__icontains=normalized_value
            )
        ).distinct()
