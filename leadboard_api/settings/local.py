from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]
SECRET_KEY = config("SECRET_KEY")
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CORS headers
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.instincthub\.com$",
    r"^https://instincthub.com$",
    r"^https://instincthub-oxyka.ondigitalocean.app$",
    "https://leadboard.instincthub.com",
    "http://localhost:3000",
    "http://localhost:3001",
]

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3001',
    'http://localhost:3000',
    "https://instincthub-oxyka.ondigitalocean.app",
]

SENDGRID_SANDBOX_MODE_IN_DEBUG = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'