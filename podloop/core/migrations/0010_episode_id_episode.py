# Generated by Django 4.2.1 on 2023-05-18 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_rename_uploade_date_episode_upload_date'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='episode',
            constraint=models.UniqueConstraint(fields=('podcast', 'title'), name='id_episode'),
        ),
    ]