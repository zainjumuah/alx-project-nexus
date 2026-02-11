import django_filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter

from .models import Product


class ProductFilter(django_filters.FilterSet):
    # I use CharFilter here so I can parse/validate category myself and return clear 400 errors.
    category = django_filters.CharFilter(method="filter_category")

    class Meta:
        model = Product
        fields = ["category"]

    def filter_category(self, queryset, name, value):
        # I wanted invalid values to fail loud/early so the API contract stays explicit.
        if value in (None, ""):
            return queryset

        try:
            category_id = int(value)
        except (TypeError, ValueError):
            raise ValidationError({"category": "Must be an integer category id."})

        if category_id <= 0:
            raise ValidationError({"category": "Must be a positive integer category id."})

        return queryset.filter(category_id=category_id)


class StableOrderingFilter(OrderingFilter):
    """
    Adds an internal tie-breaker for deterministic pagination.
    I do not expose `id` as a public ordering field in Swagger/API params.
    """

    TIE_BREAK_FIELDS = {"price", "created_at"}

    def get_ordering(self, request, queryset, view):
        # DRF validates requested ordering fields; if none is provided, this falls back to view.ordering.
        ordering = super().get_ordering(request, queryset, view)
        ordering = list(ordering or [])

        if not ordering:
            return ordering

        # I read from the end so if multiple ordering fields are passed, tie direction follows the last relevant one.
        last_relevant = next(
            (field for field in reversed(ordering) if field.lstrip("-") in self.TIE_BREAK_FIELDS),
            None,
        )
        if not last_relevant:
            return ordering

        tie_breaker = "-id" if last_relevant.startswith("-") else "id"
        normalized = {field.lstrip("-") for field in ordering}

        # I only append once to avoid weird duplicates like [..., "id", "id"].
        if "id" not in normalized:
            ordering.append(tie_breaker)

        return ordering
