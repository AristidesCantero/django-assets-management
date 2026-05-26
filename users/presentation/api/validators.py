from rest_framework.validators import UniqueValidator, ValidationError
from users.domain.models import User
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
import re


def validate_name(value):
    if isinstance(value, str) and not value.strip():
        raise ValidationError("Username cannot be empty or just whitespace.")

    if not value.isalpha():
        raise ValidationError("Username cannot have special characters.")

    return value

def validate_last_name(value):
    if isinstance(value, str) and not value.strip():
        raise ValidationError("Last name cannot be empty or just whitespace.")

    if not value.replace(" ", "").isalpha():
        raise ValidationError("Last name cannot have special characters or numbers.")

    return value
  
def validate_password(value):
  if isinstance(value, str) and not value.strip():
        raise ValidationError("Password cannot be empty or just whitespace.")

    
  if not re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', value):
    raise ValidationError("Password must at least contain one special character and have at least 8 character")
  
  if " " in value:
    raise ValidationError("The password must not contain whitespaces")
  
  return value


def validate_email_unique(value):
    value = value.strip().lower()
    try:
      validate_email(value)
    except DjangoValidationError:
      raise serializers.ValidationError('Invalid email format.')
    
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError("Email already registered.")
    return value


