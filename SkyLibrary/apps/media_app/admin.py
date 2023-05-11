from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django import forms
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required

from .models import MediaTags, Media, MediaDownload, MediaRating, Comment, CommentRating, ReportType, Report


admin.site.register(MediaDownload)
admin.site.register(MediaRating)
admin.site.register(CommentRating)


@admin.register(MediaTags)
class MediaTagsModelAdmin(admin.ModelAdmin):

    readonly_fields = ('user_who_added',)

    def add_view(self, request, form_url="", extra_context=None):

        if request.user.is_superuser:
            self.readonly_fields = ()

        else:
            self.fields = ('name_en_us', 'help_text_en_us', 'name_ru', 'help_text_ru')

        return super(MediaTagsModelAdmin, self).add_view(request, form_url, extra_context)

    def save_model(self, request, obj, form, change):

        obj.user_who_added_id = request.user.id

        super(MediaTagsModelAdmin, self).save_model(request, obj, form, change)


@admin.register(Media)
class MediaModelAdmin(admin.ModelAdmin):

    list_display = ('title', 'user_who_added', 'active', 'pub_date')

    @method_decorator(permission_required('media_app.change_media_active_field', raise_exception=True))
    def change_view(self, request, object_id, form_url="", extra_context=None):

        if not request.user.is_superuser:
            self.fields = ('active',)

        return super(MediaModelAdmin, self).change_view(request, object_id, form_url, extra_context)


class CommentModelAdminForm(forms.ModelForm):

    content = forms.ChoiceField()

    def __init__(self, *args, **kwargs):

        super(CommentModelAdminForm, self).__init__(*args, **kwargs)

        content_field_choices = (
            (self.instance.content, f'%s ({self.instance.content})' % _("Current value of the field")),
            (f'%s.' % _("This comment was banned"), _('The value of the banned field')),
        )

        self.fields['content'].choices = content_field_choices


@admin.register(Comment)
class CommentModelAdmin(admin.ModelAdmin):

    form = CommentModelAdminForm
    list_display = ('content', 'user_who_added', 'pub_date')

    @method_decorator(permission_required('media_app.change_comment_content_field_to_banned', raise_exception=True))
    def change_view(self, request, object_id, form_url="", extra_context=None):

        if not request.user.is_superuser:
            self.fields = ('content',)

        return super(CommentModelAdmin, self).change_view(request, object_id, form_url, extra_context)


@admin.register(ReportType)
class ReportTypeModelAdmin(admin.ModelAdmin):

    readonly_fields = ('user_who_added',)

    def add_view(self, request, form_url="", extra_context=None):

        if request.user.is_superuser:
            self.readonly_fields = ()

        else:
            self.fields = ('name_en_us', 'name_ru')

        return super(ReportTypeModelAdmin, self).add_view(request, form_url, extra_context)

    def save_model(self, request, obj, form, change):

        obj.user_who_added_id = request.user.id

        super(ReportTypeModelAdmin, self).save_model(request, obj, form, change)


@admin.register(Report)
class ReportModelAdmin(admin.ModelAdmin):

    list_display = ('content', 'get_link_to_target', 'pub_date')
    readonly_fields = ('get_link_to_target',)

    def get_link_to_target(self, instance):

        link = instance.get_link_to_target()

        return format_html('<a href="{0}">{0}</a>', link)

    get_link_to_target.short_description = _('Link to the target of the report')
