# Generated by Django 4.2.1 on 2023-06-09 09:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_podcastfollow_podcastfollow_id_follow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcast',
            name='followers',
        ),
    ]