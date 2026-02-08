from django.contrib import admin
from django.urls import include, path

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from products.views import CategoryViewSet, ProductViewSet


class TaggedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        tags=["Auth"],
        operation_description="Obtain JWT access and refresh tokens.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaggedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        tags=["Auth"],
        operation_description="Refresh JWT access token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaggedTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(
        tags=["Auth"],
        operation_description="Verify a JWT token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")


schema_view = get_schema_view(
    openapi.Info(
        title="ZeeCommerce API",
        default_version="v1",
        description="E-Commerce Backend API (DRF + JWT)",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/", include("users.urls")),
    path("api/auth/token/", TaggedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TaggedTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TaggedTokenVerifyView.as_view(), name="token_verify"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
