from storages.backends.s3boto3 import S3Boto3Storage
from boto3.session import Session as Boto3_Session
from botocore.client import Config

from .settings import MEDIA_STORAGE_BUCKET_NAME


class MediaStorage(S3Boto3Storage):

    bucket_name = MEDIA_STORAGE_BUCKET_NAME
    location = 'media'
    file_overwrite = False


def get_s3_connection():

    session = Boto3_Session()

    s3 = session.client(
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        config=Config(signature_version='s3v4'),
    )

    return s3
