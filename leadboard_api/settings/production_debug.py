"""
The production debug is in two ways you want to see all
the production info but also see errors if exists like a normal debug mode
"""

from .base import *

DEBUG = True

# fixme later
ALLOWED_HOSTS = ["*"]

#  read more https://docs.djangoproject.com/en/4.1/ref/middleware/#http-strict-transport-security
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600  # one hour
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
#  I JUST ONLY SET THE DATABASE FOR POSTGRES BUT IT COULD BE MODIFIED
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_DB', default=''),
        'USER': config('POSTGRES_USER', default=''),
        'PASSWORD': config('POSTGRES_PASSWORD', default=''),
        'HOST': config('POSTGRES_HOST', default=''),
        'PORT': config('POSTGRES_PORT', default=''),
    }
}

# CORS headers
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.instincthub\.com$",
    r"^https://instincthub.com$",
    r"^https://instincthub-oxyka.ondigitalocean.app$",
    "http://localhost:3000",
    "http://localhost:3001",
]
