from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["category"]
    ordering_fields = ["price"]

    def get_queryset(self):
        """
        Query optimized + strict validation for category query param type.

        Policy:
        - category missing => normal list
        - category non-integer / <=0 => 400 (explicit and consistent)
        - category integer but not found => empty results (normal filter semantics)
        """
        qs = super().get_queryset()

        raw_category = self.request.query_params.get("category")
        if raw_category is not None:
            try:
                cat_id = int(raw_category)
            except (TypeError, ValueError):
                raise ValidationError({"category": "Must be an integer category id."})
            if cat_id <= 0:
                raise ValidationError({"category": "Must be a positive integer category id."})

        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by category id (integer). Non-integer values return 400.",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by price: use 'price' or '-price'.",
                type=openapi.TYPE_STRING,
                enum=["price", "-price"],
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number (PageNumberPagination).",
                type=openapi.TYPE_INTEGER,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
