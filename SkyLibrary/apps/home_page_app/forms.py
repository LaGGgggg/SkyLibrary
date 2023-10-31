from django import forms
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, HTML
from crispy_forms.bootstrap import FormActions
from crispy_bootstrap5.bootstrap5 import FloatingField

from media_app.models import Media, MediaTags, MediaRating
from .services import RATING_DIRECTION_CHOICES


class FilterMediaForm(forms.Form):

    _rating_choices_with_empty = [i for i in MediaRating.rating_choices]
    _rating_choices_with_empty.append((-1, ''))

    _rating_direction_choices_with_empty = [i for i in RATING_DIRECTION_CHOICES]
    _rating_direction_choices_with_empty.append((-1, ''))

    TAGS_CHOICES = MediaTags.objects.all()

    title = forms.CharField(max_length=300, required=False, label=_('title'))
    author = forms.CharField(max_length=300, required=False, label=_('author'))
    tags = forms.ModelMultipleChoiceField(queryset=TAGS_CHOICES, required=False, label=_('Tags'))
    rating_minimum_value = forms.ChoiceField(
        required=False, label=_('Minimum value'), choices=_rating_choices_with_empty, initial=-1
    )
    rating_maximum_value = forms.ChoiceField(
        required=False, label=_('Maximum value'), choices=_rating_choices_with_empty, initial=-1
    )
    rating_direction = forms.ChoiceField(
        required=False, label=_('Issue procedure'), choices=_rating_direction_choices_with_empty, initial=-1
    )
    user_who_added = forms.CharField(max_length=300, required=False, label=_('user who added'))

    @property
    def helper(self):

        helper = FormHelper()

        helper.form_show_labels = False
        helper.form_id = 'filter_media_form'

        custom_form_actions_submit_button = Submit('submit', _('Filter'))

        # Needed because Submit class automatically sets btn btn-primary class and not remove it if other classes added.
        custom_form_actions_submit_button.field_classes = 'btn btn-outline-primary'

        helper.layout = Layout(
            Fieldset(
                _('Text filters:'),
                FloatingField('title', id='filter_media_form_title_field'),
                FloatingField('author', id='filter_media_form_author_field'),
                FloatingField('user_who_added', id='filter_media_form_user_who_added_field'),
            ),
            Fieldset(
                _('Tags filter:'),
                'tags',
                HTML(
                    '<section class="small ms-4">%s</section>' %
                    _('Click with pressed ctrl to select multiply or deselect')
                ),
            ),
            Fieldset(
                _('Rating filters:'),
                'rating_direction',
                'rating_minimum_value',
                'rating_maximum_value',
            ),
            FormActions(
                custom_form_actions_submit_button,
            ),
        )

        return helper
