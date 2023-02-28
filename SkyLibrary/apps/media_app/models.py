from django.db import models
from django.db.models import Avg, Count, Sum, QuerySet
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.urls import reverse

from datetime import datetime, timedelta
from logging import getLogger


logger = getLogger(__name__)

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

    INACTIVE = 0
    ACTIVE = 1
    NOT_VALID = 2

    active_choices = (
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active'),
        (NOT_VALID, 'Not valid'),
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

    class Meta:

        permissions = [
            ('change_media_active_field', _('Can change the value of the media active field')),
        ]


def get_best_active_media(amount: int) -> list[Media]:
    return sorted(Media.objects.filter(active=1), key=lambda media: media.get_rating(), reverse=True)[:amount]


class MediaDownload(models.Model):

    NOT_DOWNLOADED = 0
    DOWNLOADED = 1

    download_choices = (
        (NOT_DOWNLOADED, 'Not downloaded'),
        (DOWNLOADED, 'Downloaded'),
    )

    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='media_media_download')
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user_who_added_media_download')
    pub_date = models.DateField(auto_now_add=True)
    download = models.SmallIntegerField(choices=download_choices, default=1)

    def __str__(self):
        return f'{self.media.title}_download({self.download})'

    def clean(self, *args, **kwargs):

        try:
            if MediaDownload.objects.get(media=self.media, user_who_added=self.user_who_added):
                raise ValidationError(
                    {NON_FIELD_ERRORS: [_('Object with this user and media already exists')]},
                    code='duplicate',
                )

        except MediaDownload.DoesNotExist:
            pass

        super().clean()

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

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
        return f'{self.media.title} rating ({self.rating})'

    class Meta:
        db_table = 'media_app_media_rating'


class Comment(models.Model):

    MEDIA_TYPE = 1
    COMMENT_TYPE = 2

    target_type_choices = (
        (MEDIA_TYPE, 'Media type'),
        (COMMENT_TYPE, 'Comment type'),
    )

    content = models.CharField(max_length=500)
    target_type = models.PositiveSmallIntegerField(choices=target_type_choices)
    target_id = models.PositiveIntegerField()
    user_who_added = \
        models.ForeignKey(User, on_delete=models.SET_DEFAULT, related_name='comment', default='deleted user')
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        if self.target_type == self.MEDIA_TYPE:
            return f'Media type comment (id: {self.id})'

        elif self.target_type == self.COMMENT_TYPE:
            return f'Comment type comment (id: {self.id})'

    def clean(self, *args, **kwargs):

        try:

            latest_user_comment_pub_date: datetime = Comment.objects.filter(
                user_who_added=self.user_who_added
            ).order_by('-pub_date')[0].pub_date

            if datetime.now(latest_user_comment_pub_date.tzinfo) - latest_user_comment_pub_date < timedelta(seconds=30):
                raise ValidationError(
                    {NON_FIELD_ERRORS: [_('Too frequent comments, please wait and try again')]},
                    code='too_frequent_comments',
                )

        except IndexError:
            # IndexError means what no objects in a database (with a needed type, id and user)
            pass

        super().clean()

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def get_rating(self) -> int:
        return self.comment_comment_rating.aggregate(Sum('rating'))['rating__sum'] or 0

    def get_current_user_comment_rating(self) -> int:

        rating: int

        try:
            rating = CommentRating.objects.get(user_who_added=self.user_who_added, comment=self.id).rating

        except CommentRating.DoesNotExist:
            rating = 0

        return rating

    def get_replies(self) -> QuerySet:
        # returns all comment replies from newest to oldest

        replies: QuerySet = Comment.objects.filter(
            target_type=self.COMMENT_TYPE, target_id=self.id
        ).order_by('-pub_date')

        return replies

    class Meta:

        permissions = [
            (
                'change_comment_content_field_to_banned',
                _('Can change the content of the comment to "This comment was banned"')
            ),
        ]


class CommentRating(models.Model):

    UPVOTE = 1
    DOWNVOTE = -1

    rating_choices = (
        (UPVOTE, 'Up vote'),
        (DOWNVOTE, 'Down vote'),
    )

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_comment_rating')
    rating = models.SmallIntegerField(choices=rating_choices)
    user_who_added = models.ForeignKey(
        User,
        on_delete=models.SET_DEFAULT,
        related_name='user_who_added_comment_rating',
        default=0,
    )
    pub_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'comment (id: {self.comment.id}) rating ({self.rating})'

    def clean(self, *args, **kwargs):

        try:

            comment_rating: CommentRating = \
                CommentRating.objects.get(comment=self.comment, user_who_added=self.user_who_added)

            comment_rating.delete()

            if comment_rating.rating == self.rating:
                # do not add new record, validation error only for it
                raise ValidationError({NON_FIELD_ERRORS: ['']})

        except CommentRating.DoesNotExist:
            # If the user has no ratings (with needed comment id and vote type), they can add a new rating
            pass

        super().clean()

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'media_app_comment_rating'


def get_page_media_id_by_comment(comment: Comment) -> int:

    if comment.target_type == Comment.MEDIA_TYPE:
        return comment.target_id

    elif comment.target_type == Comment.COMMENT_TYPE:
        return get_page_media_id_by_comment(
            Comment.objects.only('id', 'target_id', 'target_type').get(id=comment.target_id)
        )


class ReportType(models.Model):

    name_en_us = models.CharField(max_length=60, unique=True)
    name_ru = models.CharField(max_length=60, unique=True)
    pub_date = models.DateField(auto_now_add=True)
    user_who_added = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='report_type')

    def __str__(self):

        if get_language() == 'ru':
            return str(self.name_ru)

        else:
            return str(self.name_en_us)

    class Meta:
        db_table = 'media_app_report_type'


class Report(models.Model):

    MEDIA_TYPE = 1
    COMMENT_TYPE = 2

    target_type_choices = (
        (MEDIA_TYPE, 'Media type'),
        (COMMENT_TYPE, 'Comment type'),
    )

    report_type = models.ManyToManyField(ReportType, related_name='report_type_report')
    content = models.CharField(max_length=300)
    target_type = models.PositiveSmallIntegerField(choices=target_type_choices)
    target_id = models.PositiveIntegerField()
    user_who_added = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='user_who_added_report', default='deleted user'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        if self.target_type == self.MEDIA_TYPE:
            return f'Media report (id: {self.id})'

        elif self.target_type == self.COMMENT_TYPE:
            return f'Comment report (id: {self.id})'

    def clean(self, *args, **kwargs):

        if Report.objects.filter(
                user_who_added=self.user_who_added,
                target_type=self.target_type,
                target_id=self.target_id,
        ).exists():
            raise ValidationError(
                {NON_FIELD_ERRORS: [_('You can not create one more report on the same media/comment')]},
                code='second_report_on_the_same_media_or_comment',
            )

        try:

            latest_user_report_pub_date: datetime = Report.objects.filter(
                user_who_added=self.user_who_added
            ).order_by('-pub_date')[0].pub_date

            if datetime.now(latest_user_report_pub_date.tzinfo) - latest_user_report_pub_date < timedelta(seconds=30):
                raise ValidationError(
                    {NON_FIELD_ERRORS: [_('Too frequent reports, please wait and try again')]},
                    code='too_frequent_reports',
                )

        except IndexError:
            # IndexError means what no objects in a database (with a needed type, id and user)
            pass

        super().clean()

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def get_link_to_target(self) -> str:

        is_media_type: bool = self.target_type == self.MEDIA_TYPE
        is_comment_type: bool = self.target_type == self.COMMENT_TYPE

        if is_media_type:
            media_id = self.target_id

        elif is_comment_type:
            media_id = get_page_media_id_by_comment(
                Comment.objects.only('id', 'target_id', 'target_type').get(id=self.target_id)
            )

        else:

            logger.error(f'Unexpected target type - "{self.target_type}"')

            raise ValidationError(
                _('Error, unexpected value, please try again or contact support (code: 3.1)'),
                code='unexpected_target_type',
            )

        base_link = reverse('view_media', kwargs={'media_id': media_id})

        if is_media_type:
            return base_link

        elif is_comment_type:
            return f"{base_link}#comment_{self.target_id}"
