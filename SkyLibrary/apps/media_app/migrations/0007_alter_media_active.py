# Generated by Django 4.1 on 2022-12-03 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media_app', '0006_alter_mediatags_help_text_en_us_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='active',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Inactive'), (1, 'Active'), (2, 'Not valid')], default=0),
        ),
    ]
