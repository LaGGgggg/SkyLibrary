from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):

    def create_superuser(self, username, email=None, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", 4)  # 4 - superuser

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if extra_fields.get("role") != 4:  # 4 - superuser
            raise ValueError("Superuser must have role=4.")  # 4 - superuser

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):

    objects = CustomUserManager()

    VISITOR = 1
    MODERATOR = 2
    ADMIN = 3
    SUPERUSER = 4

    ROLE_CHOICES = (
        (VISITOR, 'Visitor'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
        (SUPERUSER, 'Superuser'),
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES)
