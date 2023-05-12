from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 4)  # 4 - superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('role') != 4:  # 4 - superuser
            raise ValueError('Superuser must have role=4.')  # 4 - superuser

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):

    objects = CustomUserManager()

    VISITOR = 1
    MODERATOR = 2
    ADMIN = 3
    SUPERUSER = 4

    ROLE_CHOICES = (
        (VISITOR, _('Visitor')),
        (MODERATOR, _('Moderator')),
        (ADMIN, _('Admin')),
        (SUPERUSER, _('Superuser')),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, verbose_name=_('role'))
    email = models.EmailField(verbose_name=_('email'), unique=True, blank=False, null=False)

    class Meta(AbstractUser.Meta):

        permissions = [
            ('add_moderator', _('Can add a new moderator')),
            ('change_moderator', _('Can change a moderator data')),
            ('change_user_active_field', _('Can change the user active field')),
        ]
