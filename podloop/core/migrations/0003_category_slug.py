# Generated by Django 4.2.1 on 2023-05-15 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_notificationmodel_remove_episode_link_thumbnail_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.CharField(max_length=100, null=True, unique=True),
        ),
    ]
