from django import forms
from django.contrib.auth import get_user_model

from django_registration.forms import RegistrationFormUniqueEmail


class CustomSignUpForm(RegistrationFormUniqueEmail):

    # Don't change the form name(role), it's important for the html page.
    role = forms.IntegerField(widget=forms.HiddenInput(), disabled=True, initial=1)

    class Meta(RegistrationFormUniqueEmail.Meta):

        model = get_user_model()
        fields = RegistrationFormUniqueEmail.Meta.fields + ['role']
