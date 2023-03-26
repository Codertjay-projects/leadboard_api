from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    this is used for s3 bucket to set the location to the media files
    there is a place on the production.py where i called:

    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
    """
    location = settings.MEDIAFILES_LOCATION