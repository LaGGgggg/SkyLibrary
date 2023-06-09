from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django_registration.forms import RegistrationFormUniqueEmail

from media_app.models import MediaRating


User = get_user_model()


class CustomSignUpForm(RegistrationFormUniqueEmail):

    # Don't change the form name(role), it's important for the html page.
    role = forms.IntegerField(widget=forms.HiddenInput(), label=_('role'), disabled=True, initial=User.VISITOR)

    class Meta(RegistrationFormUniqueEmail.Meta):

        model = User
        fields = RegistrationFormUniqueEmail.Meta.fields + ['role']


class CreateOrUpdateMediaRating(forms.ModelForm):

    def rating_clean(self):

        rating = self.cleaned_data['rating']

        if rating not in MediaRating.rating_choices_list:
            raise ValidationError(
                _('Select a valid choice. That choice is not one of the available choices.'), code='bad_choice'
            )

        return rating

    class Meta:

        model = MediaRating

        fields = ['media', 'user_who_added', 'rating']
