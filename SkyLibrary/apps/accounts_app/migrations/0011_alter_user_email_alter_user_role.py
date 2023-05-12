# Generated by Django 4.2.1 on 2023-05-12 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts_app', '0010_alter_user_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Visitor'), (2, 'Moderator'), (3, 'Admin'), (4, 'Superuser')], verbose_name='role'),
        ),
    ]
