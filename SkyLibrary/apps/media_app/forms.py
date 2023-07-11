from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import Media, MediaTags, ReportType


class CreateOrUpdateMediaForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=MediaTags.objects.all(),
    )

    def _is_update(self) -> bool:
        return True if self.instance else False

    def clean_title(self):

        title = self.cleaned_data['title']

        if self._is_update():
            filtered_media = Media.objects.exclude(id=self.instance.id).filter(title=title)

        else:
            filtered_media = Media.objects.filter(title=title)

        if filtered_media.exists():
            raise ValidationError(_('Not a unique title, change it.'), code='invalid')

        else:
            return title

    def clean_description(self):

        description = self.cleaned_data['description']

        if self._is_update():
            filtered_media = Media.objects.exclude(id=self.instance.id).filter(description=description)

        else:
            filtered_media = Media.objects.filter(description=description)

        if filtered_media.exists():
            raise ValidationError(_('Not a unique description, change it.'), code='invalid')

        else:
            return description

    def _check_object_size(self, object_name, max_object_size):

        checking_object = self.cleaned_data[f'{object_name}']

        if checking_object:

            if checking_object.size > max_object_size:

                max_size_in_megabytes = int(max_object_size / 1024 / 1024)

                validation_error_message = \
                    _('{checking_object_name} - is too big (more than {max_size_in_megabytes}Mb)')

                raise ValidationError(
                    validation_error_message.format(
                        checking_object_name=checking_object.name, max_size_in_megabytes=max_size_in_megabytes
                    ),
                    code='invalid',
                )

        return checking_object

    def clean_file(self):
        # 3221225472 = 1024 * 1024 * 1024 * 3 = 3 * 1024Mb = 3072Mb (Mb value should be integer, not 7.5Mb)
        return self._check_object_size('file', 3221225472)

    def clean_cover(self):
        # 7340032 = 1024 * 1024 * 7 = 7Mb (Mb value should be integer, not 7.5Mb)
        return self._check_object_size('cover', 7340032)

    class Meta:

        model = Media

        fields = ['title', 'description', 'author', 'tags', 'file', 'cover']


class CreateCommentForm(forms.Form):

    content = forms.CharField(max_length=500, label=_('Comment text'))

    @property
    def helper(self):

        helper = FormHelper()

        helper.form_show_labels = False
        helper.form_id = 'create_media_comment_form'
        helper.attrs['data-request-type'] = 'create_comment'

        custom_form_actions_submit_button = Submit('submit', _('Add comment'), css_id='create_media_comment_button')

        # Needed because Submit class automatically sets btn btn-primary class and not remove it if other classes added.
        custom_form_actions_submit_button.field_classes = 'btn btn-outline-primary'

        helper.layout = Layout(
            FloatingField('content', id='add_media_comment_content_field'),
            FormActions(
                custom_form_actions_submit_button,
            ),
        )

        return helper


class CreateReplyCommentForm(forms.Form):

    content = forms.CharField(max_length=500, label=_('Reply text'))

    @property
    def helper(self):

        helper = FormHelper()

        helper.form_show_labels = False
        helper.form_id = 'under_comment_form'
        helper.attrs['data-request-type'] = 'create_comment'

        custom_form_actions_submit_button = Submit('submit', _('Add reply'), css_id='under_comment_form_submit_button')

        # Needed because Submit class automatically sets btn btn-primary class and not remove it if other classes added.
        custom_form_actions_submit_button.field_classes = 'btn btn-outline-primary'

        helper.layout = Layout(
            FloatingField('content', id='under_comment_form_content_field'),
            FormActions(
                custom_form_actions_submit_button,
            ),
        )

        return helper


class CreateReportCommentForm(forms.Form):

    report_type = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=ReportType.objects.all(),
        label=f'{_("Report reason")}:',
    )
    content = forms.CharField(max_length=300, label=f'{_("What is happened")}?')

    @property
    def helper(self):

        helper = FormHelper()

        helper.form_id = 'under_comment_form'
        helper.form_class = 'border border-info'
        helper.attrs['data-request-type'] = 'create_report'

        custom_form_actions_submit_button = \
            Submit('submit', _('Send report'), css_id='under_comment_form_submit_button')

        # Needed because Submit class automatically sets btn btn-primary class and not remove it if other classes added.
        custom_form_actions_submit_button.field_classes = 'btn btn-outline-primary'

        helper.layout = Layout(
            Field('report_type', id='under_comment_form_report_type_field'),
            FloatingField('content', wrapper_class='ms-2', id='under_comment_form_content_field'),
            FormActions(
                custom_form_actions_submit_button,
            ),
        )

        return helper

    def clean_report_type(self):

        report_types: QuerySet = self.cleaned_data['report_type']

        for report_type in report_types:

            try:
                ReportType.objects.get(id=report_type.id)

            except ReportType.DoesNotExist:
                raise ValidationError(_('Select the correct report reason choice.'), code='invalid_choice')

        return self.cleaned_data['report_type']


class CreateReportMediaForm(CreateReportCommentForm):

    @property
    def helper(self):

        helper = FormHelper()

        helper.form_id = 'media_report_form'
        helper.form_class = 'border border-info'
        helper.attrs['data-request-type'] = 'create_report'

        custom_form_actions_submit_button = \
            Submit('submit', _('Send report'), css_id='media_report_form_submit_button')

        # Needed because Submit class automatically sets btn btn-primary class and not remove it if other classes added.
        custom_form_actions_submit_button.field_classes = 'btn btn-outline-primary'

        helper.layout = Layout(
            Field('report_type', id='media_report_form_report_type_field'),
            FloatingField('content', wrapper_class='ms-2', id='media_report_form_content_field'),
            FormActions(
                custom_form_actions_submit_button,
            ),
        )

        return helper
