from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.core.files import File
from django.core.files.images import ImageFile
from .models import *
import os,json

def load_data():
    #####CATEGORIES####
    BASE_PATH = os.getcwd() + '/core/data/'
    if(Category.objects.all().count() == 0):
        with open(BASE_PATH+'categories.json', 'r') as file:
            categories = json.load(file)
        for category in categories:
            Category.objects.create(name=category['name'],slug=category['slug'])
        print('Categories created')
        

    ####USERS####
    User = get_user_model()
    if(User.objects.all().count() == 0):
        with open(BASE_PATH+'users.json', 'r') as file:
            users = json.load(file)

        # Iterate over the user profiles
        for user in users:                
            new_user = User()
            new_user.id = user['id']
            new_user.name = user['name']
            new_user.last_name = user['last_name']
            new_user.email = user['email']
            new_user.set_password(user['password'])
            new_user.username = user['username']
            new_user.is_active = True
            new_user.is_email_verified = True
            if user['is_superuser'] == 1:
                new_user.is_superuser = True
                new_user.is_staff = True
            if user['is_creator'] == 1:
                new_user.is_creator = True
            new_user.save()
        print('Users created')
        
        
    ####PODCASTS####
    if(Podcast.objects.all().count() == 0):
        with open(BASE_PATH+'podcasts.json', 'r') as file:
            podcasts = json.load(file)

        # Iterate over the podcasts 
        for podcast in podcasts:
            new_podcast = Podcast()
            new_podcast.name = podcast['name']
            new_podcast.description = podcast['description']
            new_podcast.owner_id = podcast['owner_id']
            new_podcast.slug = slugify(podcast['name'])
            with open(BASE_PATH+'images/'+podcast['podcast_thumbnail'], 'rb') as image_file:
                file_image = ImageFile(image_file)
                new_podcast.podcast_thumbnail.save(podcast['podcast_thumbnail'],file_image)
            new_podcast.save()
            for category in podcast["categories"]:
                new_podcast.categories.add(Category.objects.get(name=category))
            new_podcast.save()
        print('Podcasts created')
        
    ####EPISODES####
    if(Episode.objects.all().count() == 0):
        with open(BASE_PATH+'episodes.json', 'r') as file:
            episodes = json.load(file)
        
        # Iterate over the episodes 
        for episode in episodes:
            new_episode = Episode()
            new_episode.id = episode['id']
            new_episode.title = episode['title']
            new_episode.description = episode['description']
            new_episode.podcast = Podcast.objects.get(name=episode['podcast'])
            new_episode.slug = episode['slug']
            new_episode.is_private = episode['is_private']
            new_episode.length = episode['length']
            with open(BASE_PATH+'images/'+episode['episode_thumbnail'], 'rb') as image_file:
                file_image = ImageFile(image_file)
                new_episode.episode_thumbnail.save(episode['episode_thumbnail'],file_image)
                
            with open(BASE_PATH+'audios/'+episode['audio'], 'rb') as audio_file:
                file_audio = File(audio_file)
                new_episode.audio.save(episode['audio'],file_audio)
            new_episode.save()  
        print('Episodes created')
        
    if(EpisodeComment.objects.all().count() == 0):
        with open(BASE_PATH+'comments.json', 'r') as file:
            comments = json.load(file)
        for comment in comments:
            episode = Episode.objects.get(id=comment['episode_id'])
            owner = User.objects.get(id=comment['owner'])
            new_comment = EpisodeComment()
            new_comment.id = comment['id']
            new_comment.text = comment['comment']
            new_comment.episode = episode
            new_comment.owner = owner
            new_comment.save()
        print('Comments created')