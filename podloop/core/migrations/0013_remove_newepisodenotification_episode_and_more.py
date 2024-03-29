# Generated by Django 4.2.1 on 2023-06-08 17:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_episodecomment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episodecomment',
            name='episode',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='core.episode'),
        ),
        migrations.DeleteModel(
            name='ActionOnCommentNotification',
        ),
        migrations.DeleteModel(
            name='NewEpisodeNotification',
        ),
        migrations.DeleteModel(
            name='NotificationModel',
        ),
        migrations.DeleteModel(
            name='NotificationType',
        ),
    ]
