from .base import *
import os
from decouple import config


DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = []

#CORS_ALLOW_ALL_ORIGINS = True  # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# Required so Django's CSRF Origin/Referer check accepts requests that
# carry an Origin header from the consuming frontend/service.
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / "static/",
]

MEDIA_ROOT = BASE_DIR / 'static/images'

MEDIA_URL = '/images/'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_NAME_LOCAL'),
        'USER': config('POSTGRES_USER_LOCAL'),
        'PASSWORD': config('POSTGRES_PASSWORD_LOCAL'),
        'HOST': 'localhost',
        'PORT': 5434,
    },
   # 'default':{
   #   'ENGINE': 'django.db.backends.postgresql',
   #     'NAME': config('POSTGRES_NAME_LOCAL'),
   #     'USER': config('POSTGRES_USER_LOCAL'),
   #     'PASSWORD': config('POSTGRES_PASSWORD_LOCAL'),
   #     'HOST': 'localhost',
   #     'PORT': 5434,
   # },

    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },

}