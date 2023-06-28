from django.urls import path
from .views import Home,CategoryListView,CategoryDetailView,PodcastView,FollowPodcast,UnfollowPodcast,EpisodeView,ProfileView,CreatorView,BecomeCreator,PodcastEditView,PodcastEpisodeUpload,EditEpisodeView,PlaylistCreateView,PlaylistEditView,PlaylistView,DeleteEpisodeFromPlaylist,PlaylistDeleteView,Search,Feed,PodcastAnalytics,HomePage
from .models import *
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.images import ImageFile
import os,json
app_name = "core"

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
load_data()


urlpatterns = [
    path('', HomePage, name='homepage'),
    path('home', Home.as_view(), name='home'),
    path('categories', CategoryListView.as_view(), name='categories'),
    path('categories/<slug:slug>', CategoryDetailView, name='category-detail'),
    path('podcasts/<slug:slug>', PodcastView, name='podcast'),
    path('podcasts/<slug:slug>/analytics', login_required(PodcastAnalytics), name='podcast-analytics'),
    path('podcasts/<slug:slug>/edit', login_required(PodcastEditView.as_view()), name='podcast-edit'),
    path('podcasts/<slug:slug>/upload', login_required(PodcastEpisodeUpload.as_view()), name='podcast-upload'),
    path('podcasts/<slug:slug>/follow', login_required(FollowPodcast), name='follow'),
    path('podcasts/<slug:slug>/unfollow', login_required(UnfollowPodcast), name='unfollow'),
    path('podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>', EpisodeView, name='episode'),
    path('podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/edit', login_required(EditEpisodeView.as_view()), name='episode-edit'),
    path('profile', login_required(ProfileView.as_view()), name='profile'),
    path('profile/creator-studio', login_required(CreatorView.as_view()), name='creator'),
    path('profile/become-creator', login_required(BecomeCreator), name='become-creator'),
    path('profile/playlists/create', login_required(PlaylistCreateView.as_view()), name='playlist-create'),
    path('profile/playlists/<int:playlist_id>', PlaylistView, name='playlist'),
    path('profile/playlists/<int:playlist_id>/edit', login_required(PlaylistEditView.as_view()), name='playlist-edit'),
    path('profile/playlists/<int:playlist_id>/delete', login_required(PlaylistDeleteView), name='playlist-delete'),
    path('profile/playlists/<int:playlist_id>/remove/<int:episode_id>', login_required(DeleteEpisodeFromPlaylist), name='playlist-episode-remove'),
    path('search', Search, name='search'),
    path('feed', login_required(Feed), name='feed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

