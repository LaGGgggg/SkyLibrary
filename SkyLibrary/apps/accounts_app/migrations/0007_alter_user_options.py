# Generated by Django 4.1 on 2023-02-26 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts_app', '0006_alter_user_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('add_moderator', 'Can add a new moderator'), ('deactivate_user', 'Can deactivate any user')], 'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]
