from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import User


class CustomUserCreationForm(UserCreationForm):

    # Moderator, because an administrator can only add moderators
    role = forms.IntegerField(widget=forms.HiddenInput(), disabled=True, initial=User.MODERATOR)
    is_staff = forms.BooleanField(widget=forms.HiddenInput(), disabled=True, initial=True)
    email = forms.EmailField(label=_('Email address'))

    class Meta(UserCreationForm.Meta):
        model = User


@admin.register(User)
class UserUserAdmin(UserAdmin):

    fieldsets_for_superuser = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'role',
                    'user_permissions',
                ),
            }
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    fieldsets_for_admin = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active',)}),
    )
    fieldsets = ()

    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'role', 'is_staff', 'email'),
            },
        ),
    )
    list_display = ('username', 'role')

    def get_queryset(self, request):

        queryset = super(UserUserAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return queryset

        else:
            return queryset.exclude(role=User.SUPERUSER).exclude(role=User.ADMIN)

    def add_view(self, request, form_url='', extra_context=None):

        if request.user.has_perm('accounts_app.add_moderator'):
            return super(UserUserAdmin, self).add_view(request, form_url, extra_context)

        else:
            raise PermissionDenied

    def change_view(self, request, object_id, form_url='', extra_context=None):

        if request.user.is_superuser:
            self.fieldsets = self.fieldsets_for_superuser

        if request.user.role == User.ADMIN:

            self.fieldsets = self.fieldsets_for_admin

            target_user = User.objects.get(id=object_id)

            if not(request.user.has_perm('accounts_app.change_moderator') and target_user.role == User.MODERATOR):

                if request.user.has_perm('accounts_app.change_user_active_field'):
                    self.fieldsets = ((None, {'fields': ('is_active',)}),)

                else:
                    self.fieldsets = ()

        return super(UserUserAdmin, self).change_view(request, object_id, form_url, extra_context)
