# Generated by Django 4.2.1 on 2023-05-12 13:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import media_app.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media_app', '0016_alter_comment_options_alter_commentrating_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.CharField(max_length=500, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='target_id',
            field=models.PositiveIntegerField(verbose_name='target id'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='target_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Media type'), (2, 'Comment type')], verbose_name='target type'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user_who_added',
            field=models.ForeignKey(default='deleted user', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='comment', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='commentrating',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_comment_rating', to='media_app.comment', verbose_name='comment'),
        ),
        migrations.AlterField(
            model_name='commentrating',
            name='pub_date',
            field=models.DateField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='commentrating',
            name='rating',
            field=models.SmallIntegerField(choices=[(1, 'Up vote'), (-1, 'Down vote')], verbose_name='rating'),
        ),
        migrations.AlterField(
            model_name='commentrating',
            name='user_who_added',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='user_who_added_comment_rating', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='media',
            name='active',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (2, 'Not valid')], default=0, verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='media',
            name='author',
            field=models.CharField(max_length=30, verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='media',
            name='cover',
            field=models.ImageField(blank=True, null=True, upload_to=media_app.models.get_cover_upload, verbose_name='cover'),
        ),
        migrations.AlterField(
            model_name='media',
            name='description',
            field=models.TextField(unique=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='media',
            name='file',
            field=models.FileField(upload_to=media_app.models.get_file_upload, verbose_name='file'),
        ),
        migrations.AlterField(
            model_name='media',
            name='pub_date',
            field=models.DateField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='media',
            name='tags',
            field=models.ManyToManyField(related_name='tags_media', to='media_app.mediatags', verbose_name='tags'),
        ),
        migrations.AlterField(
            model_name='media',
            name='title',
            field=models.CharField(max_length=60, unique=True, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='media',
            name='user_who_added',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_who_added_media', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='mediadownload',
            name='download',
            field=models.SmallIntegerField(choices=[(0, 'Not downloaded'), (1, 'Downloaded')], default=1, verbose_name='download'),
        ),
        migrations.AlterField(
            model_name='mediadownload',
            name='media',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_media_download', to='media_app.media', verbose_name='media'),
        ),
        migrations.AlterField(
            model_name='mediadownload',
            name='pub_date',
            field=models.DateField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='mediadownload',
            name='user_who_added',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_who_added_media_download', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='mediarating',
            name='media',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_media_rating', to='media_app.media', verbose_name='media'),
        ),
        migrations.AlterField(
            model_name='mediarating',
            name='pub_date',
            field=models.DateField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='mediarating',
            name='rating',
            field=models.SmallIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], verbose_name='rating'),
        ),
        migrations.AlterField(
            model_name='mediarating',
            name='user_who_added',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_who_added_media_rating', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='mediatags',
            name='help_text_en_us',
            field=models.CharField(max_length=80, unique=True, verbose_name='help text en-us'),
        ),
        migrations.AlterField(
            model_name='mediatags',
            name='help_text_ru',
            field=models.CharField(max_length=80, unique=True, verbose_name='help text ru'),
        ),
        migrations.AlterField(
            model_name='mediatags',
            name='name_en_us',
            field=models.CharField(max_length=16, unique=True, verbose_name='name en-us'),
        ),
        migrations.AlterField(
            model_name='mediatags',
            name='name_ru',
            field=models.CharField(max_length=16, unique=True, verbose_name='name ru'),
        ),
        migrations.AlterField(
            model_name='mediatags',
            name='pub_date',
            field=models.DateField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='mediatags',
            name='user_who_added',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='media_tags', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='report',
            name='content',
            field=models.CharField(max_length=300, verbose_name='content'),
        ),
        migrations.AlterField(
            model_name='report',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='report',
            name='report_type',
            field=models.ManyToManyField(related_name='report_type_report', to='media_app.reporttype', verbose_name='report type'),
        ),
        migrations.AlterField(
            model_name='report',
            name='target_id',
            field=models.PositiveIntegerField(verbose_name='target id'),
        ),
        migrations.AlterField(
            model_name='report',
            name='target_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Media type'), (2, 'Comment type')], verbose_name='target type'),
        ),
        migrations.AlterField(
            model_name='report',
            name='user_who_added',
            field=models.ForeignKey(default='deleted user', on_delete=django.db.models.deletion.SET_DEFAULT, related_name='user_who_added_report', to=settings.AUTH_USER_MODEL, verbose_name='user who added'),
        ),
        migrations.AlterField(
            model_name='reporttype',
            name='name_en_us',
            field=models.CharField(max_length=60, unique=True, verbose_name='name en-us'),
        ),
        migrations.AlterField(
            model_name='reporttype',
            name='name_ru',
            field=models.CharField(max_length=60, unique=True, verbose_name='name ru'),
        ),
        migrations.AlterField(
            model_name='reporttype',
            name='pub_date',
            field=models.DateField(auto_now_add=True, verbose_name='publication date'),
        ),
        migrations.AlterField(
            model_name='reporttype',
            name='user_who_added',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='report_type', to=settings.AUTH_USER_MODEL, verbose_name='user who addded'),
        ),
    ]