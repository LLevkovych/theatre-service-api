from django.core.mail import send_mail
from django.conf import settings

def send_verification_email(user, token):
    verification_url = f"{settings.FRONTEND_URL}/verify-email/?token={token}"
    subject = "Confirm your email"
    message = f"Please click the link to verify your email: {verification_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
