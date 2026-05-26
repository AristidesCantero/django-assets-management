from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from users.models import User
from django.template.loader import render_to_string
from django.conf import settings
import os

class TokenGenerator:
    def __init__(self):
        self.email_template = "email_template.html"

    def send_mail(self, user, token, uid) -> int:
        """
        Send an email with the token url using the HTML email template.
        
        Returns: the number of successfull emails, since is 1 email there are only 0 or 1
        """
        verification_email = f"http://localhost:8000/users/confirma/?uid={uid}&token={token}"
        # Render the HTML template with the user and token
        html_message = render_to_string(self.email_template, {
            'user_name': user,
            'verification_email': verification_email,
        })

        # Send the email
        return send_mail(
                subject='Your Verification Token',
                message='',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email.strip()],
                html_message=html_message,
                fail_silently=False,
        )


def generate_uid(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid


def send_verification_email(user, token):
    if not isinstance(user, User):
        raise TypeError("instance to send email is not User")

    uid = generate_uid(user)

    token_generator = TokenGenerator()
    return token_generator.send_mail(user, token, uid)
