# Generated by Django 4.2.1 on 2023-05-11 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff_app', '0004_alter_moderatortask_media'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='moderatortask',
            options={'verbose_name': 'moderator task', 'verbose_name_plural': 'moderator tasks'},
        ),
    ]