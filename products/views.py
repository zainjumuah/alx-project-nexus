from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


PRODUCT_LIST_PARAMETERS = [
    openapi.Parameter(
        "category",
        openapi.IN_QUERY,
        description="Filter products by category id.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
    openapi.Parameter(
        "ordering",
        openapi.IN_QUERY,
        description="Sort by price or created_at using 'price', '-price', 'created_at', or '-created_at'.",
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
        description="Results per page, if page-size query is enabled.",
        type=openapi.TYPE_INTEGER,
        required=False,
    ),
]


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
        description="Results per page, if page-size query is enabled.",
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
            "List products (public). Use query parameters for filtering and ordering.\n"
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
        tags=["Products"],
        operation_description="Update a product (JWT required).",
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

    # I removed DjangoFilterBackend because I'm already validating and filtering
    # by category in get_queryset, and I didn't want two systems doing the same job.
    filter_backends = [OrderingFilter]
    # I kept ordering explicit so Swagger docs and backend behavior stay aligned.
    ordering_fields = ["price", "created_at"]
    ordering = ["price"]

    def get_queryset(self):
        qs = Product.objects.select_related("category").all()
        raw_category = self.request.query_params.get("category")
        if raw_category is not None:
            try:
                cat_id = int(raw_category)
            except (TypeError, ValueError):
                raise ValidationError({"category": "Must be an integer category id."})
            if cat_id <= 0:
                raise ValidationError({"category": "Must be a positive integer category id."})
            # I filter directly here so bad values fail fast and valid values are always applied.
            qs = qs.filter(category_id=cat_id)

        return qs


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
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
