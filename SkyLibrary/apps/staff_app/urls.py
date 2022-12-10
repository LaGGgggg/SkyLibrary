from django.urls import path

from .views import ViewModeratorPage

urlpatterns = [
    path('moderator/', ViewModeratorPage.as_view(), name='moderator_page'),
]
