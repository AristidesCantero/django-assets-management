from rest_framework.validators import UniqueValidator, ValidationError
from users.models import User


def validate_name(value):
    if isinstance(value, str) and not value.strip():
        raise ValidationError("Username cannot be empty or just whitespace.")

    if not value.isalpha():
        raise ValidationError("Username cannot have special characters.")

    if User.objects.filter(username=value).exists():
        raise ValidationError("A user with that username already exists.")
    return value

def validate_last_name(value):
    if isinstance(value, str) and not value.strip():
        raise ValidationError("Last name cannot be empty or just whitespace.")

    if not value.replace(" ", "").isalpha():
        raise ValidationError("Last name cannot have special characters or numbers.")

    return value


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError("A user with that email already exists.")
    return value


