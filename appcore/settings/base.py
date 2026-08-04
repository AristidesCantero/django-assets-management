
from pathlib import Path
import os
from datetime import timedelta
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')
JWT_SIGNING_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)

# SECURITY WARNING: don't run with debug turned on in production!



# Application definition

BASE_APPS = [
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] 

LOCAL_APPS = [
    'assets.apps.AssetsConfig',
    'protocol.apps.ProtocolConfig',
    'components.apps.ComponentsConfig',
    'locations.apps.LocationsConfig',
    'users.apps.UsersConfig',
    'permissions.apps.PermissionsConfig',
]

THIRD_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'simple_history',
    'drf_yasg',
    'django_extensions',
    
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS


# NOTE: The global CsrfViewMiddleware is intentionally replaced by
# AdminOnlyCsrfMiddleware below. CSRF protection for API views is enforced
# per-view through the CookieJWTAuthentication class
# (permissions/domain/authentication.py), which is the default DRF
# authentication. AdminOnlyCsrfMiddleware keeps Django admin (/admin/)
# CSRF-protected while still running CSRF request preparation and cookie
# writing for API views (get_token()/rotate_token() flag the cookie).
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'appcore.middleware.AdminOnlyCsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF Configuration
# The CSRF secret travels in a plain cookie (CSRF_USE_SESSIONS=False), so
# JWT statelessness is preserved.
# IMPORTANT: CSRF_COOKIE_HTTPONLY=True is safe here because there is no SPA:
# the consuming service reads the token from the response body of the
# csrf-token endpoint, not from the cookie via JavaScript.
CSRF_USE_SESSIONS = False
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_AGE = 31449600  # 1 year, mirrors Django's default
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
#CSRF_FAILURE_VIEW = 'appcore.errors.csrf_failure_json'


ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost', cast=lambda v: [s.strip() for s in v.split(',')])
#if this is used then not need to use `CORS_ALLOWED_ORIGINS` because it will allow all the origins
# CORS_ALLOWED_ORIGINS_REGEX = [
#     "http://localhost:3000",
# ]

ROOT_URLCONF = 'appcore.urls'

APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        "DIRS": [
            BASE_DIR / "accounts/templates/",
            BASE_DIR / "users/templates/",
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'appcore.wsgi.application'

RUNSCRIPT_SCRIPT_DIR = [
    BASE_DIR.parent / "tools/scripts/",
]


#Django Rest Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'permissions.domain.authentication.CookieJWTAuthentication',
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    #"EXCEPTION_HANDLER": "appcore.errors.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
      'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/min',
        'anon': '20/min',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME':timedelta(minutes=200),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_COOKIE':"access_token",
    'AUTH_COOKIE_HTTP_ONLY':True,
    'AUTH_COOKIE_SAMESITE':"Lax",
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#STMP Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

