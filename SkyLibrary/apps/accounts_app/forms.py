from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class SignUpForm(UserCreationForm):

    # Don't change the form name(role), it's important for the html page.
    role = forms.IntegerField(widget=forms.HiddenInput(), disabled=True, initial=1)
    email = forms.CharField(max_length=254)

    class Meta(UserCreationForm.Meta):

        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('role', 'email')
