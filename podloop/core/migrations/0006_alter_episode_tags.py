# Generated by Django 4.2.1 on 2023-05-16 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_episode_podcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='episodes', to='core.tag'),
        ),
    ]
