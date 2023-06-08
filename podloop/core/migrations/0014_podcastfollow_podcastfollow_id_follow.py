# Generated by Django 4.2.1 on 2023-06-08 18:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0013_remove_newepisodenotification_episode_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PodcastFollow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.podcast')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'PodcastFollows',
            },
        ),
        migrations.AddConstraint(
            model_name='podcastfollow',
            constraint=models.UniqueConstraint(fields=('user', 'podcast'), name='id_follow'),
        ),
    ]