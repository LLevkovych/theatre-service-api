import urllib

from django.conf import settings
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from user.serializers import (
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)
from user.models import User
from user.tokens import EMAIL_CONFIRMATION_SALT


def generate_email_confirmation_token(user):
    data = {"user_id": user.pk}
    token = dumps(data)
    return token


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        token = generate_email_confirmation_token(user)
        encoded_token = urllib.parse.quote(token)
        confirm_url = f"{settings.FRONTEND_URL}/verify-email/{encoded_token}/"
        subject = "Confirm your email"
        message = f"Please confirm your email by clicking the link: {confirm_url}"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token is None:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = []

    def get(self, request, token):
        import logging
        logging.warning(f"Received token: {token}")

        token = urllib.parse.unquote(token)
        logging.warning(f"Decoded token: {token}")

        try:
            data = loads(token, salt=EMAIL_CONFIRMATION_SALT, max_age=60 * 60 * 24)
            logging.warning(f"Loaded data: {data}")

            user_id = data.get("user_id")
            user = User.objects.get(pk=user_id)
            if user.is_email_verified:
                return Response({"detail": "Email already confirmed."}, status=status.HTTP_200_OK)

            user.is_email_verified = True
            user.save()
            return Response({"detail": "Email confirmed successfully."}, status=status.HTTP_200_OK)
        except SignatureExpired:
            return Response({"detail": "Confirmation link has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except (BadSignature, User.DoesNotExist) as e:
            logging.warning(f"Verification failed: {e}")
            return Response({"detail": "Invalid confirmation token."}, status=status.HTTP_400_BAD_REQUEST)
