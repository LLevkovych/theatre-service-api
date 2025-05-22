from drf_spectacular.utils import OpenApiExample
from rest_framework import serializers


class RegisterRequestSchema(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterResponseSchema(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    is_email_verified = serializers.BooleanField()


class ChangePasswordRequestSchema(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class ProfileResponseSchema(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    is_email_verified = serializers.BooleanField()
    is_staff = serializers.BooleanField()


class LogoutRequestSchema(serializers.Serializer):
    refresh = serializers.CharField()


class VerifyEmailResponseSchema(serializers.Serializer):
    detail = serializers.CharField()
