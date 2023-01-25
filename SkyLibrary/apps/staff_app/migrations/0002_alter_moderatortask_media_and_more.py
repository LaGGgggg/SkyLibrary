# Generated by Django 4.1 on 2022-12-03 12:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media_app', '0007_alter_media_active'),
        ('staff_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderatortask',
            name='media',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_moderator_task', to='media_app.media', unique=True),
        ),
        migrations.AlterField(
            model_name='moderatortask',
            name='user_who_added',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_who_added_moderator_task', to=settings.AUTH_USER_MODEL, unique=True),
        ),
    ]