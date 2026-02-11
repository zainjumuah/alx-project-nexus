from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import ProductFilter, StableOrderingFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


# I keep these centralized so product list docs stay aligned with real query behavior.
PRODUCT_LIST_PARAMETERS = [
    openapi.Parameter(
        "category",
        openapi.IN_QUERY,
        description="Filter products by category id. Invalid values return 400.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "ordering",
        openapi.IN_QUERY,
        description=(
            "Sort results using: price, -price, created_at, -created_at. "
            "Tie-breaking is deterministic internally for stable pagination."
        ),
        type=openapi.TYPE_STRING,
        enum=["price", "-price", "created_at", "-created_at"],
        required=False,
    ),
    openapi.Parameter(
        "page",
        openapi.IN_QUERY,
        description="Page number.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "page_size",
        openapi.IN_QUERY,
        description="Results per page.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
]


# I keep category params separate so product/category docs can evolve independently later.
CATEGORY_LIST_PARAMETERS = [
    openapi.Parameter(
        "page",
        openapi.IN_QUERY,
        description="Page number.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "page_size",
        openapi.IN_QUERY,
        description="Results per page.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["Products"],
        manual_parameters=PRODUCT_LIST_PARAMETERS,
        operation_description=(
            "List products (public).\n"
            "Example: GET /api/products/?category=1&ordering=price&page=1"
        ),
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["Products"],
        operation_description="Retrieve a single product (public).",
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["Products"],
        operation_description="Create a product (JWT required).",
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["Products"],         operation_description="Update a product (JWT required).",
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["Products"],
        operation_description="Partially update a product (JWT required).",
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["Products"],
        operation_description="Delete a product (JWT required).",
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # I chain DjangoFilterBackend + custom ordering backend:
    # category filtering stays explicit, and ordering gets deterministic tie-breaking.
    filter_backends = [DjangoFilterBackend, StableOrderingFilter]
    filterset_class = ProductFilter

    # I keep public ordering options unchanged; `id` is only an internal tie-breaker.
    ordering_fields = ["price", "created_at"]
    ordering = ["price"]

    def get_queryset(self):
        # I use select_related so list responses don't trigger N+1 queries when serializer reads category fields.
        return Product.objects.select_related("category").order_by("price", "id")

@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        tags=["Categories"],
        manual_parameters=CATEGORY_LIST_PARAMETERS,
        operation_description="List categories (public).",
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        tags=["Categories"],
        operation_description="Retrieve a single category (public).",
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        tags=["Categories"],
        operation_description="Create a category (JWT required).",
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        tags=["Categories"],
        operation_description="Update a category (JWT required).",
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        tags=["Categories"],
        operation_description="Partially update a category (JWT required).",
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        tags=["Categories"],
        operation_description="Delete a category (JWT required).",
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    # I added id as a secondary sort so categories with same name still paginate consistently.
    queryset = Category.objects.all().order_by("name", "id")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
