from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        tags=["Auth"],
        operation_description="Register a new user account.",
    ),
)
class RegisterView(generics.CreateAPIView):
    # I'll just leave this public on purpose so first-time users can create accounts.
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
