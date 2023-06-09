from django.urls import path
from django.views.generic import TemplateView

from .views import ViewCreateMedia, ViewViewMedia, ViewUpdateMedia

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
]
