from django.urls import path
from django.views.generic import TemplateView

from .views import ViewCreateMedia, ViewViewMedia, ViewUpdateMedia, S3AuthMultipartGetDataForUploadView, \
    S3AuthMultipartGetUploadPartPresignedUrlView, S3AuthMultipartDoCompleteView, S3AuthMultipartDoAbortView

urlpatterns = [
    path('create/', ViewCreateMedia.as_view(), name='create_media'),
    path(
        'create_successful/',
        TemplateView.as_view(template_name='media_app/create_media_successful.html'),
        name='create_media_successful',
    ),
    path('view/<int:media_id>/', ViewViewMedia.as_view(), name='view_media'),
    path('update/<int:media_id>/', ViewUpdateMedia.as_view(), name='update_media'),
    path(
        'update_successful/',
        TemplateView.as_view(template_name='media_app/update_media_successful.html'),
        name='update_media_successful',
    ),
    path(
        'create_or_update/s3auth/get_data_for_upload/<str:file_name>/',
        S3AuthMultipartGetDataForUploadView.as_view(),
        name='s3auth_multipart_get_data_for_upload',
    ),
    path(
        'create_or_update/s3auth/get_upload_part_presigned_url/<str:upload_id>/<int:part_number>/<path:file_key>/',
        S3AuthMultipartGetUploadPartPresignedUrlView.as_view(),
        name='s3auth_multipart_get_upload_part_presigned_url',
    ),
    path(
        'create_or_update/s3auth/do_abort/<str:upload_id>/<path:file_key>/',
        S3AuthMultipartDoAbortView.as_view(),
        name='s3auth_multipart_do_abort',
    ),
    path(
        'create_or_update/s3auth/do_complete/<str:upload_id>/<path:file_key>/',
        S3AuthMultipartDoCompleteView.as_view(),
        name='s3auth_multipart_do_complete',
    ),
]
