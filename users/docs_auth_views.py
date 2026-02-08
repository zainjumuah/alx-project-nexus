from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


# I moved these wrappers out of urls.py so routes stay cleaner.
class TokenObtainPairViewDocs(TokenObtainPairView):
    @swagger_auto_schema(
        tags=["Auth"],
        operation_description="Obtain JWT access + refresh tokens.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshViewDocs(TokenRefreshView):
    @swagger_auto_schema(
        tags=["Auth"],
        operation_description="Refresh JWT access token using a refresh token.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenVerifyViewDocs(TokenVerifyView):
    @swagger_auto_schema(
        tags=["Auth"],
        operation_description="Verify a JWT token is valid.",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
