from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["email_verified"]
        extra_kwargs = {"mobile": {"required": False}}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
            "email": {"required": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), username=username, password=password)

        if not user:
            msg = " unable to log in with provided credentials"
            raise serializers.ValidationError(msg, code="authorization")

        if not user.profile.email_verified:
            raise serializers.ValidationError("Email not verified.", code="authorization")
        attrs["user"] = user
        return attrs
