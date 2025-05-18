from django.core.signing import BadSignature, SignatureExpired
from django.core.signing import dumps, loads
from user.models import User
import urllib.parse


EMAIL_CONFIRMATION_SALT = "email-confirmation-salt"

def generate_email_confirmation_token(user):
    data = {"user_id": user.pk}
    token = dumps(data, salt=EMAIL_CONFIRMATION_SALT)
    return urllib.parse.quote(token)

def verify_email_confirmation_token(token):
    try:
        token = urllib.parse.unquote(token)
        data = loads(token, salt=EMAIL_CONFIRMATION_SALT, max_age=60*60*24)
        user_id = data.get("user_id")
        return User.objects.get(pk=user_id)
    except (BadSignature, SignatureExpired, User.DoesNotExist):
        return None
