from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings

signer = TimestampSigner()

def generate_email_verification_token(user):
    value = f"{user.pk}:{user.email}"
    return signer.sign(value)

def verify_email_verification_token(token, max_age=60*60*24):  # 1 день
    try:
        value = signer.unsign(token, max_age=max_age)
        user_id, email = value.split(":")
        return int(user_id), email
    except (BadSignature, SignatureExpired):
        return None, None
