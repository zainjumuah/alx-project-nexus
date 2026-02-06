from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core import exceptions

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    # I set trim_whitespace=False so I don't 'fix' some innocent user's passwd
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta: 
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"email": {"required": False, "allow_blank": True}}

    def validate_username(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Username is required")
        return value
    
    def validate_email(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            return None
        return User.objects.normalize_email(value)
    
    def validate_password(self, value: str) -> str:
        try:
            user = User(
                username=(self.initial_data.get("username") or "").strip(),
                email=(self.initial_data.get("email") or "").strip() or None,
            )
            validate_password(value, user=user)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"]
        )
