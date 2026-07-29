from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from users.domain.service.base import BaseService


class BaseTokenGenerator(BaseService):
  
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