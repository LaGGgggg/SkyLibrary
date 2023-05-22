from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions
from crispy_bootstrap5.bootstrap5 import FloatingField

from media_app.models import Media, MediaTags


class SearchMediaForm(forms.Form):

    text = forms.CharField(max_length=100, required=False, label=_('Text'))
    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=MediaTags.objects.all(),
        required=False,
        label=_('Tags'),
    )

    def clean(self):

        cleaned_data = super().clean()

        try:

            cleaned_data['text']  # check key existing
            text = True

        except KeyError:
            text = False

        if text and not cleaned_data['text']:

            try:

                if not cleaned_data['tags']:
                    self.add_error(None, _('Please specify any text or tags to search for'))  # None - non field error

            except KeyError:
                # KeyError => no tags
                self.add_error(None, _('Please specify any text or tags to search for'))  # None - non field error

        return cleaned_data

    @property
    def helper(self):

        helper = FormHelper()

        helper.form_show_labels = False
        helper.form_id = 'search_media_form'

        custom_form_actions_submit_button = Submit('submit', _('Search'))

        # Needed because Submit class automatically sets btn btn-primary class and not remove it if other classes added.
        custom_form_actions_submit_button.field_classes = 'btn btn-outline-primary'

        helper.layout = Layout(
            FloatingField('text', id='search_media_form_text_field'),
            Field('tags'),
            FormActions(
                custom_form_actions_submit_button,
            ),
        )

        return helper
