# Generated by Django 4.1 on 2022-10-07 12:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import media_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, unique=True)),
                ('description', models.TextField(unique=True)),
                ('author', models.CharField(max_length=30)),
                ('pub_date', models.DateField(auto_now_add=True)),
                ('active', models.PositiveSmallIntegerField(choices=[(0, 'In moderation'), (1, 'Active'), (2, 'Inactive')], default=0)),
                ('file', models.FileField(upload_to=media_app.models.get_file_upload)),
                ('cover', models.ImageField(blank=True, null=True, upload_to=media_app.models.get_cover_upload)),
                ('user_who_added', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='media', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MediaRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateField(auto_now_add=True)),
                ('rating', models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_media_rating', to='media_app.media')),
                ('user_who_added', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_who_added_media_rating', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'media_app_media_rating',
            },
        ),
        migrations.CreateModel(
            name='MediaDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateField(auto_now_add=True)),
                ('download', models.SmallIntegerField(choices=[(0, 'Not downloaded'), (1, 'Downloaded')], default=1)),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_media_download', to='media_app.media')),
                ('user_who_added', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_who_added_media_download', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'media_app_media_download',
            },
        ),
    ]
