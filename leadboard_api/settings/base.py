"""
Django settings for leadboard_api project.

Generated by 'django-admin startproject' using Django 4.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import datetime
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from decouple import config
from .installed import INSTALLED_APPS
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# Application definition

INSTALLED_APPS = INSTALLED_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "maintenance_mode.middleware.MaintenanceModeMiddleware",  # maintenance mode middleware (must be the las)
]

ROOT_URLCONF = "leadboard_api.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "leadboard_api.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#  Changing default django user models
AUTH_USER_MODEL = 'users.User'

# change the default auth serializer for token and get user details
REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'users.serializers.UserDetailSerializer',
    'JWTSerializer': 'users.serializers.TokenSerializer',
}

#  change the default register serializer
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'users.serializers.CustomRegisterSerializer',
}

# custom function used to add extra functionality to the signup process
# kind of using it to create a user just let me say the save method function
ACCOUNT_ADAPTER = 'users.adapters.UserAdapter'

# setup for django allauth authentications
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
# Not currently using allauth to manage verification
ACCOUNT_EMAIL_VERIFICATION = 'none'
# for removing extra subject from message if using allauth to send mail
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

#  the default rest framework setting
# anon is for the AnonRateThrottle base on anonymous user
#  is for the UserRateThrottle base on logged-in user
# ScopedRateThrottle this is just used to set custom throttle just like the authentication, monitor below
REST_FRAMEWORK = {
    #  default pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],

    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/min',
        'user': '200/min',
        # the throttle is the amount of time a user can access a route in a minute
        'authentication': '3/min',
        # used on route where the user is not logged in like requesting otp
        'monitor': '3/min',
    },
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # currently setting the default authentication for django rest framework to jwt
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# telling rest framework to use jwt
REST_USE_JWT = True

# this is used by the package djangorestframework-simplejwt==5.2.0 for providing
# jwt authentication and also modifying the time which the token expires
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=10),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    'SIGNING_KEY': SECRET_KEY
}

APPEND_SLASH = True

#  configuration for celery
CELERY_ENABLED = True
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"
# Send test mail and other bugs info
ADMINS = [("Afenikhena Favour", ("dev.codertjay@gmail.com"))]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    "leadboard-sk-header",
    "company-id"
]

#  fixme : later set cache to be redis or memcache
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'leadboard_api_cackhe_table',
#     }
# }

# maintenance mode
MAINTENANCE_MODE_TEMPLATE = "errors/503.html"
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True

# EMAIL CONFIGURATION
EMAIL_BACKEND = config('EMAIL_BACKEND')
SENDGRID_API_KEY = config('SENDGRID_API_KEY')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

