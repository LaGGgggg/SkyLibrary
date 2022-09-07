from django.urls import path
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView

from .views import SignUpView, view_profile

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='sign_up'),
    path('login/', LoginView.as_view(template_name='accounts_app/login.html'), name='login'),
    path('profile/', view_profile, name='profile'),
    path('logout_successful/', TemplateView.as_view(template_name='accounts_app/logout_successful.html'))
]
