from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView


class CustomPasswordResetView(PasswordResetView):

    template_name = 'accounts_app/password_reset.html'
    email_template_name = 'accounts_app/password_reset_email.html'
    success_url = reverse_lazy('password_reset_successful')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):

    template_name = 'accounts_app/password_reset_confirm.html'
    success_url = reverse_lazy('custom_password_reset_complete')


class CustomPasswordChangeView(PasswordChangeView):

    template_name = 'accounts_app/password_change.html'
    success_url = reverse_lazy('password_change_successful')


@login_required()
def view_profile(request):
    return render(request, 'accounts_app/profile.html')
