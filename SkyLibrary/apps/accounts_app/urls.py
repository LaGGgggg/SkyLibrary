from django.urls import path, re_path
from django.contrib.auth.views import LoginView
from django.views.generic.base import TemplateView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView

from .views import (
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    CustomPasswordChangeView,
    view_profile
)

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts_app/login.html'), name='login'),
    path('profile/', view_profile, name='profile'),
    path(
        'logout_successful/', TemplateView.as_view(template_name='accounts_app/logout_successful.html'),
        name='logout_successful'
    ),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path(
        'password_reset_successful/',
        PasswordResetDoneView.as_view(template_name='accounts_app/password_reset_successful.html'),
        name='password_reset_successful',
    ),
    re_path(
        '^password_reset_confirm/(?P<uidb64>[-\\w]+)/(?P<token>[-:\\w]+)/$',
        CustomPasswordResetConfirmView.as_view(),
        name='custom_password_reset_confirm',
    ),
    path(
        'password_reset_complete/',
        PasswordResetCompleteView.as_view(template_name='accounts_app/password_reset_complete.html'),
        name='custom_password_reset_complete',
    ),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path(
        'password_change_successful/',
        TemplateView.as_view(template_name='accounts_app/password_change_successful.html'),
        name='password_change_successful',
    ),
]
