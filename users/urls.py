from django.urls import path

from .docs_auth_views import (
    TokenObtainPairViewDocs,
    TokenRefreshViewDocs,
    TokenVerifyViewDocs,
)
from .views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("token/", TokenObtainPairViewDocs.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshViewDocs.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyViewDocs.as_view(), name="token_verify"),
]
