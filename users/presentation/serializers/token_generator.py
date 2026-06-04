from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from users.models import User
from django.template.loader import render_to_string
from django.conf import settings
import os


class BaseTokenGenerator:
  
  def __init__(self, email_template):
    self.email_template = email_template
  
  
  def send_email(self, render_dict: dict, subject, user):
        html_message = render_to_string(self.email_template, render_dict)

        # Send the email
        return send_mail(
                subject=subject,
                message='',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email.strip()],
                html_message=html_message,
                fail_silently=False,
        )



class TokenGenerator(BaseTokenGenerator):
    def __init__(self, email_template=None):
        email_template = email_template or "email_template.html"
        super().__init__(email_template)

    def send_email(self, user, token, uid) -> int:
        """
        Send an email with the token url using the HTML email template.
        Returns: the number of successfull emails, since is 1 email there are only 0 or 1
        """
        verification_link = f"http://localhost:8000/users/confirma/?uid={uid}&token={token}"
        subject = "Assets App verificación de usuario"
        render_dict = {
            'user_name': user.name,
            'verification_link': verification_link,
        }

        #send the email with parent class 
        return super().send_email(render_dict,subject,user)



class TokenInvitationGenerator(BaseTokenGenerator):
  
    def __init__(self, email_template=None):
        email_template = email_template or "email_template.html"
        super().__init__(email_template)

    def send_email(self, user, token, uid, business_uid, business,inviter_user) -> int:
        """
        Send an email with the token url using the HTML email template.
        Returns: the number of successfull emails, since is 1 email there are only 0 or 1
        """
        invitation_url = f"http://localhost:8000/users/accept-invitation/?uid={uid}&token={token}&business={business_uid}"
        user_name = user.name
        business_name = business.name
        inviter_name = inviter_user.name
        subject = "Assets App verificación de usuario"
        render_dict = {invitation_url,business_name, inviter_name, user_name
        }

        #send the email with parent class 
        return super().send_email(render_dict,subject,user)


def generate_uid(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid


def send_invitation_email(user,token, business, inviter):
    if not isinstance(user, User):
        raise TypeError("instance to send email is not User")
      
    uid = generate_uid(user)
    business_uid = generate_uid(business)
    token_generator = TokenInvitationGenerator()
    return token_generator.send_mail(user, token, uid, business_uid, business, inviter)
    

def send_verification_email(user, token):
    if not isinstance(user, User):
        raise TypeError("instance to send email is not User")

    uid = generate_uid(user)

    token_generator = TokenGenerator()
    return token_generator.send_mail(user, token, uid)
