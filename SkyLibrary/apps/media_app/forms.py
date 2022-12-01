from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Media, MediaTags


class CreateMediaForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=MediaTags.objects.all(),
    )

    def clean_title(self):

        title = self.cleaned_data['title']

        if Media.objects.filter(title=title):
            raise ValidationError(_('Not a unique title, change it.'), code='invalid')

        else:
            return title

    def clean_description(self):

        description = self.cleaned_data['description']

        if Media.objects.filter(description=description):
            raise ValidationError(_('Not a unique description, change it.'), code='invalid')

        else:
            return description

    def _check_object_size(self, object_name, max_object_size):

        checking_object = self.cleaned_data[f'{object_name}']

        if checking_object:

            if checking_object.size > max_object_size:
                max_cover_size_in_megabytes = int(max_object_size / 1024 / 1024)

                raise ValidationError(
                    _(f'{checking_object.name} - is too big (more than {max_cover_size_in_megabytes}Mb)'),
                    code='invalid',
                )

        return checking_object

    def clean_file(self):
        # 419430400 = 1024 * 1024 * 400 = 400Mb (Mb value should be integer, not 7.5Mb)
        return self._check_object_size('file', 419430400)

    def clean_cover(self):
        # 7340032 = 1024 * 1024 * 7 = 7Mb (Mb value should be integer, not 7.5Mb)
        return self._check_object_size('cover', 7340032)

    class Meta:

        model = Media

        fields = ['title', 'description', 'author', 'tags', 'file', 'cover']
