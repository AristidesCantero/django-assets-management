from .base import *
import os
from decouple import config


DEBUG = config('DEBUG')

ALLOWED_HOSTS = []


#CORS_ALLOW_ALL_ORIGINS = True  # If this is used then `CORS_ALLOWED_ORIGINS` will not have any effect
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
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
        'NAME': config('POSTGRES_NAME_PRODUCTION'),
        'USER': config('POSTGRES_USER_PRODUCTION'),
        'PASSWORD': config('POSTGRES_PASSWORD_PRODUCTION'),
        'HOST': config('POSTGRES_HOST_PRODUCTION'),
        'PORT': config('POSTGRES_PORT_PRODUCTION'),
    },

    'sqlite': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },

    # 'mysql_db' : {
    #     'ENGINE': 'django.db.backends.mysql',
    #     "NAME": "mysql_dbtest",
    #     "USER": "aristides",
    #     "PASSWORD": "AristidesCantero",
    #     "HOST": "localhost",
    #     "PORT": "3306",
    #     "TEST": {
    #         "NAME": "test_dbtest",
    #     },
    # }

}