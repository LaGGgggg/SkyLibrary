from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language

User = get_user_model()


class MediaTags(models.Model):

    name_en_us = models.CharField(max_length=16, unique=True)
    help_text_en_us = models.CharField(max_length=80, unique=True)

    name_ru = models.CharField(max_length=16, unique=True)
    help_text_ru = models.CharField(max_length=80, unique=True)

    pub_date = models.DateField(auto_now_add=True)
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='media_tags')

    def __str__(self):

        if get_language() == 'ru':
            return str(self.name_ru)

        else:
            return str(self.name_en_us)

    class Meta:
        db_table = 'media_app_media_tag'


def get_file_upload(instance, filename: str) -> str:
    return f'media_app/{instance.author}/{instance.title}.{filename.split(".")[-1]}'


def get_cover_upload(instance, filename: str) -> str:
    return f'media_app/{instance.author}/{instance.title}_cover.{filename.split(".")[-1]}'


class Media(models.Model):

    active_choices = (
        (0, 'Inactive'),
        (1, 'Active'),
        (2, 'Not valid'),
    )

    title = models.CharField(max_length=60, unique=True)
    description = models.TextField(unique=True)
    author = models.CharField(max_length=30)
    pub_date = models.DateField(auto_now_add=True)
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_who_added_media')
    tags = models.ManyToManyField(MediaTags, related_name='tags_media')
    active = models.PositiveSmallIntegerField(choices=active_choices, default=0)
    file = models.FileField(upload_to=get_file_upload)
    cover = models.ImageField(upload_to=get_cover_upload, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_downloads_number(self) -> int:
        return self.media_media_download.aggregate(Count('download'))['download__count']

    def get_rating(self) -> float | int:
        return round(self.media_media_rating.aggregate(Avg('rating'))['rating__avg'] or 0, 2)


class MediaDownload(models.Model):

    download_choices = (
        (0, 'Not downloaded'),
        (1, 'Downloaded'),
    )

    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='media_media_download')
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_who_added_media_download')
    pub_date = models.DateField(auto_now_add=True)
    download = models.SmallIntegerField(choices=download_choices, default=1)

    def clean(self, *args, **kwargs):

        try:
            if MediaDownload.objects.get(media=self.media, user_who_added=self.user_who_added):
                raise ValidationError({NON_FIELD_ERRORS: [_('Object with this user and media already exists')]})

        except MediaDownload.DoesNotExist:
            pass

        super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.media.title}_download({self.download})'

    class Meta:
        db_table = 'media_app_media_download'


class MediaRating(models.Model):

    rating_choices = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    )

    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='media_media_rating')
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_who_added_media_rating')
    pub_date = models.DateField(auto_now_add=True)
    rating = models.SmallIntegerField(choices=rating_choices)

    def __str__(self):
        return f'{self.media.title}_rating({self.rating})'

    class Meta:
        db_table = 'media_app_media_rating'
