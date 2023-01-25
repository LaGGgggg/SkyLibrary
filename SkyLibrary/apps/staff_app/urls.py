from django.urls import path

from .views import ViewModeratorPage

urlpatterns = [
    path(
        'moderator/<str:get_next_task>/<str:from_view_media_page>/', ViewModeratorPage.as_view(), name='moderator_page'
    ),
]
