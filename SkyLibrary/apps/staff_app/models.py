from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from media_app.models import Media

User = get_user_model()


class ModeratorTask(models.Model):

    media = models.OneToOneField(Media, on_delete=models.CASCADE, related_name='media_moderator_task', unique=True)
    user_who_added = \
        models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_who_added_moderator_task', unique=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.media.title} %s' % _("moderator task")

    class Meta:

        db_table = 'staff_app_moderator_task'
        verbose_name = _('moderator task')
        verbose_name_plural = _('moderator tasks')
