from django.urls import path

from .views import ViewIndex

urlpatterns = [
    path('', ViewIndex.as_view(), name='index'),
]
