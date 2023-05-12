# Generated by Django 4.2.1 on 2023-05-12 13:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('media_app', '0017_alter_comment_content_alter_comment_pub_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff_app', '0005_alter_moderatortask_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderatortask',
            name='create_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='create date'),
        ),
        migrations.AlterField(
            model_name='moderatortask',
            name='media',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='media_moderator_task', to='media_app.media', verbose_name='media'),
        ),
        migrations.AlterField(
            model_name='moderatortask',
            name='user_who_added',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_who_added_moderator_task', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
    ]
