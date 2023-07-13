from storages.backends.s3boto3 import S3Boto3Storage

from .settings import MEDIA_STORAGE_BUCKET_NAME


class MediaStorage(S3Boto3Storage):

    bucket_name = MEDIA_STORAGE_BUCKET_NAME
    location = 'media'
    file_overwrite = False
