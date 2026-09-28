import django_filters
from django.db.models import Q
from paradedb.functions import Score
from paradedb.search import ParadeDB, Term

from .models import BaseModel, Vehicle


class BaseModelFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    q = django_filters.CharFilter(method="filter_search")
    make = django_filters.UUIDFilter(field_name="make_id")
    model = django_filters.CharFilter(field_name="model", lookup_expr="iexact")
    year = django_filters.NumberFilter(field_name="year")
    assembly_country = django_filters.CharFilter(
        field_name="model_vehicles__assembly_country",
        lookup_expr="iexact",
        distinct=True,
    )

    class Meta:
        model = BaseModel
        fields = ["search", "q", "make", "model", "year", "assembly_country"]

    def filter_search(self, queryset, _name, value):
        normalized_value = (value or "").strip()
        if not normalized_value:
            return queryset
        search_query = ParadeDB(
            Term(normalized_value.lower(), prefix=True, distance=0)
        )
        return (
            queryset.filter(
                Q(model=search_query) | Q(generation=search_query)
            )
            .annotate(score=Score())
            .order_by("-score")
        )


class VehicleFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")
    q = django_filters.CharFilter(method="filter_search")
    model = django_filters.UUIDFilter(field_name="model_id")
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
            "powertrain",
            "transmission",
            "variant_name",
        ]

    def filter_search(self, queryset, _name, value):
        normalized_value = (value or "").strip()
        if not normalized_value:
            return queryset
        search_query = ParadeDB(
            Term(normalized_value.lower(), prefix=True, distance=0)
        )
        matching_model_ids = list(
            BaseModel.objects.filter(model=search_query).values_list(
                "pk", flat=True
            )
        )
        return (
            queryset.filter(
                Q(variant_name=search_query) | Q(model_id__in=matching_model_ids)
            )
            .annotate(score=Score())
            .order_by("-score")
        )
