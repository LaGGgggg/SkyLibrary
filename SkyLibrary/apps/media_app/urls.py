from django.urls import path
from django.views.generic import TemplateView

from .views import ViewCreateMedia

urlpatterns = [
    path('create/', ViewCreateMedia.as_view(), name='create_media'),
    path(
        'create_successful/',
        TemplateView.as_view(template_name='media_app/create_media_successful.html'),
        name='create_media_successful',
    ),
]
