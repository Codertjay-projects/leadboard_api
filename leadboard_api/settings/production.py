from .base import *

DEBUG = False

ALLOWED_HOSTS = ["leadapi.instincthub.com"]

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

# Cache database
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# CORS headers
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://\w+\.instincthub\.com$",
    r"^https://instincthub.com$",
    r"^https://instincthub-oxyka.ondigitalocean.app$",
    "https://leadboard.instincthub.com",
    "https://leadboard-nextjs-17nqm9sjw-instincthub.vercel.app"
]

##############################################
# Django S3 Bucket setup
# This is to set you default upload to use
# your S3 bucket which is either digital ocean/AWS

# The ID from aws or Digital ocean Spaces
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
# The Secretkey for aws or Digital ocean secret key
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
# The bucket name We're trying to use
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
# The endpoint url
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL')
# This is used to prevent the files from being overwritten if exists
AWS_S3_FILE_OVERWRITE = False

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
# This enables user to be able to read the file
AWS_DEFAULT_ACL = 'public-read'

AWS_S3_SIGNATURE_VERSION = "s3v4"

# Location to set the media file
MEDIAFILES_LOCATION = 'instincthub_apis_media'
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

#####################################################
