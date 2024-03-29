# Generated by Django 4.2.1 on 2023-07-16 11:37

from django.db import migrations, models
import media_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('media_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='cover',
            field=models.ImageField(blank=True, max_length=300, null=True, upload_to=media_app.models.get_upload, verbose_name='cover'),
        ),
        migrations.AlterField(
            model_name='media',
            name='file',
            field=models.FileField(max_length=300, upload_to=media_app.models.get_upload, verbose_name='file'),
        ),
    ]
