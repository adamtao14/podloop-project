# Generated by Django 4.2.1 on 2023-05-17 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_episode_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='episode',
            name='length',
            field=models.IntegerField(default=0),
        ),
    ]
