from django.urls import path

from .views import ViewModeratorPage, ViewRedirectToModeratorPage

urlpatterns = [
    path(
        'moderator/<str:get_next_task>/<str:from_view_media_page>/', ViewModeratorPage.as_view(), name='moderator_page'
    ),
    path('moderator/', ViewRedirectToModeratorPage.as_view(), name='redirect_to_moderator_page'),
]
