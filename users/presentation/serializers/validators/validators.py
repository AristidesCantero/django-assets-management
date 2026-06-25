

from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission
from rest_framework.validators import UniqueValidator, ValidationError
from permissions.domain.permission_classes.permissions import *
from permissions.domain.models import BusinessMembership
from rest_framework import serializers
from users.domain.models import User
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
  
def validate_email(value):
  if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
  if User.objects.filter(username=value).exists():
      raise serializers.ValidationError("A user with that username already exists.")
  
  return value


def validate_businessmembership(instance, business_id):
  if not isinstance(instance, (str,int)):
    raise ValidationError(f"BusinessMembership id has a incorrect type")
  
  db_businessmembership = BusinessMembership.objects.filter(id=instance, business=business_id).first()
  if not db_businessmembership:
    raise ValidationError("Business Membership not found")
  
  return str(instance)

def validate_userbusinesspermission(instance, user_id):

  if not isinstance(instance, dict):
    raise ValidationError("Incorrect format recieved, permissions are expected to be in a dictionary")
  
  recievedpermissions = instance.keys()
  
  permissions = Permission.objects.filter(id_in=recievedpermissions).values_list("id",flat=True)
  
  non_existing_ids = set(recievedpermissions) - permissions
  
  if non_existing_ids:
    raise ValidationError(f"Invalid permissions ids: {", ".join(non_existing_ids)}")
  
  return instance
  
  
  
  
  
  
  return instance