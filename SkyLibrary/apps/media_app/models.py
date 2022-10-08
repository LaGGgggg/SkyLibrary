from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model

User = get_user_model()


def get_file_upload(instance, filename):
    return f'media_app/{instance.author}/{instance.title}'


def get_cover_upload(instance, filename):
    return f'media_app/{instance.author}/{instance.title}_cover'


class Media(models.Model):

    active_choices = (
        (0, 'In moderation'),
        (1, 'Active'),
        (2, 'Inactive'),
    )

    title = models.CharField(max_length=60, unique=True)
    description = models.TextField(unique=True)
    author = models.CharField(max_length=30)
    pub_date = models.DateField(auto_now_add=True)
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='media')
    active = models.PositiveSmallIntegerField(choices=active_choices, default=0)
    file = models.FileField(upload_to=get_file_upload)
    cover = models.ImageField(upload_to=get_cover_upload, null=True, blank=True)

    def __str__(self):
        return self.title

    def get_downloads_number(self):
        return self.media_media_download.aggregate(Count('download'))['download__count']

    def get_rating(self):
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
