from logging import getLogger

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import FormActions
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import Media, MediaTags, ReportType
from app_main.s3_storage import get_s3_connection


logger = getLogger(__name__)


class CreateOrUpdateMediaForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=MediaTags.objects.all(),
        label=_('Tags'),
    )
    file = forms.FileField(required=False, label=_('File'))
    file_key = forms.CharField(required=False, max_length=300, widget=forms.HiddenInput())

    def _is_update(self) -> bool:
        return True if self.instance.title else False

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

    def clean_cover(self):
        return self._check_object_size('cover', settings.COVER_UPLOAD_MAX_SIZE)

    def clean_file_key(self) -> None | str:

        error_message = _(
            'Something went wrong, you may not have specified the file field, please try again or contact support'
        )

        try:

            file_key = self.cleaned_data['file_key']

            if not file_key:

                if not self._is_update():
                    self.add_error(None, ValidationError(error_message, code='required'))

                return

            if settings.IS_TEST:  # USED FOR TESTING PURPOSES ONLY!!!

                logger.warning('The IS_TEST variable is used. It can only be used for testing purposes!')

                return file_key  # local storage, not s3

            else:

                s3 = get_s3_connection()

                s3_objects = [i['Key'] for i in s3.list_objects(Bucket=settings.MEDIA_STORAGE_BUCKET_NAME)['Contents']]

                if file_key in s3_objects:
                    return file_key

                else:

                    self.add_error(None, ValidationError(error_message, code='file_not_exists_in_s3_storage'))

                    return

        except KeyError:

            self.add_error(None, ValidationError(error_message, code='required'))

            return

    def clean(self):

        if settings.IS_UPDATE_MEDIA_POST_NEED_CLEAN_FILE_FIELD:  # USED FOR TESTING PURPOSES ONLY!!!

            logger.warning(
                'The IS_UPDATE_MEDIA_POST_NEED_CLEAN_FILE_FIELD variable is used.'
                ' It can only be used for testing purposes!'
            )

            self.cleaned_data['file'] = None

        if self._is_update():

            try:
                if file_key := self.cleaned_data['file_key']:
                    file_key = file_key.replace(settings.MEDIA_URL.replace('/', '', 1), '')

            except KeyError:
                file_key = None

            try:
                file = self.cleaned_data['file']

            except KeyError:
                file = None

            if file_key and not file:
                # file changed
                self.cleaned_data['file'] = file_key

            elif not file_key and file:
                # file has not changed
                pass

            else:

                error_message = _(
                    'Something went wrong with your request, please try again or contact support (code: {error_code})'
                )

                self.add_error(None, ValidationError(error_message.format(error_code='6.2'), code='invalid'))

            media_id = self.instance.id

            cache_keys = [
                make_template_fragment_key('view_media_page_viewer_content_1', [media_id]),
                make_template_fragment_key('view_media_page_viewer_content_3'),
                make_template_fragment_key('view_media_page_viewer_content_5', [media_id]),
            ]

            for language in settings.LANGUAGES:

                language_code = language[0]

                cache_keys.append(
                    make_template_fragment_key('view_media_page_header', [media_id, language_code])
                )

                cache_keys.append(
                    make_template_fragment_key('view_media_page_viewer_content_2', [media_id, language_code])
                )

                cache_keys.append(
                    make_template_fragment_key('view_media_page_viewer_content_4', [language_code])
                )

                cache_keys.append(
                    make_template_fragment_key('view_media_page_viewer_content_6', [media_id, language_code])
                )

            cache.delete_many(cache_keys)

        else:
            if file_key := self.cleaned_data['file_key']:

                # media/media_app/vnfuewbfubfjkdkfkfkkdfkfkkfeke/24527bd7-e4f7-4c76-9bc9-2a188fec11cb.txt ->
                # -> media_app/vnfuewbfubfjkdkfkfkkdfkfkkfeke/24527bd7-e4f7-4c76-9bc9-2a188fec11cb.txt
                file_key = file_key.replace(settings.MEDIA_URL.replace('/', '', 1), '')

                file = self.cleaned_data['file']

                if not file:
                    # the file should not be sent to a django server
                    self.cleaned_data['file'] = file_key  # add the file key (the file already on a storage server)

                else:

                    error_message = _(
                        'Something went wrong with your request,'
                        ' please try again or contact support (code: {error_code})'
                    )

                    self.add_error(None, ValidationError(error_message.format(error_code='6.1'), code='invalid'))

        return super().clean()

    class Meta:

        model = Media

        fields = ['title', 'description', 'author', 'tags', 'file', 'file_key', 'cover']


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
