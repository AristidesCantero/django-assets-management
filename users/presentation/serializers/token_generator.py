from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from users.models import User

def generate_verification_token(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    return uid, token
  
  
def send_verification_email(user):
    if not isinstance(user, User):
        raise TypeError("instance to send email is not User")
  
    uid, token = generate_verification_token(user)

    verification_url = (
        f"http://localhost:3000/verify-email/"
        f"?uid={uid}&token={token}"
    )

    send_mail(
        subject="Verify your account",
        message=f"Click to verify: {verification_url}",
        from_email=None,
        recipient_list=[user.email],
        fail_silently=False,
    )