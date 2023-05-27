from django.urls import path
from .views import home
from .views import CategoryListView,CategoryDetailView,PodcastView,FollowView,UnfollowView,EpisodeView,ProfileView,CreatorView,BecomeCreator,PodcastEditView,PodcastEpisodeUpload,EditEpisodeView,PlaylistCreateView,PlaylistEditView,PlaylistView,DeleteEpisodeFromPlaylist,PlaylistDeleteView,Search,Feed
from .models import *
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import os,json
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
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
    if(User.objects.all().count() == 1):
        with open(BASE_PATH+'users.json', 'r') as file:
            users = json.load(file)

        # Iterate over the user profiles
        for user in users:
            new_user = User()
            new_user.name = user['name']
            new_user.last_name = user['last_name']
            new_user.email = user['email']
            new_user.set_password(user['password'])
            new_user.username = user['username']
            new_user.is_active = True
            new_user.is_email_verified = True
            new_user.save()
        print('Users created')
        
        
    ####PODCASTS####
    if(Podcast.objects.all().count() == 0):
        with open(BASE_PATH+'podcasts.json', 'r') as file:
            podcasts = json.load(file)

        # Iterate over the user profiles
        for podcast in podcasts:
            new_podcast = Podcast()
            new_podcast.name = podcast['name']
            new_podcast.description = podcast['description']
            new_podcast.owner_id = podcast['owner_id']
            new_podcast.slug = slugify(podcast['name'])
            new_podcast.save()
            for category in podcast["categories"]:
                new_podcast.categories.add(Category.objects.get(name=category))
            new_podcast.save()
        print('Podcasts created')
        
     ####FOLLOWS####
    if(Podcast.objects.all().count() == 0):
        with open(BASE_PATH+'following.json', 'r') as file:
            follows = json.load(file)

        # Iterate over the user profiles
        for follow in follows:
            for podcast in follow["followed_podcasts"]:
                podcast_object = Podcast.objects.get(name=podcast)
                podcast_object.followers.add(User.objects.get(email=follow["email"]))
                podcast_object.save()
           
        print('Followings created')
    
#load_data()


urlpatterns = [
    path('home', home, name='home'),
    path('categories', CategoryListView.as_view(), name='categories'),
    path('categories/<slug:slug>', CategoryDetailView, name='category-detail'),
    path('podcasts/<slug:slug>', PodcastView, name='podcast'),
    path('podcasts/<slug:slug>/edit', login_required(PodcastEditView.as_view()), name='podcast-edit'),
    path('podcasts/<slug:slug>/upload', login_required(PodcastEpisodeUpload.as_view()), name='podcast-upload'),
    path('podcasts/<slug:slug>/follow', login_required(FollowView), name='follow'),
    path('podcasts/<slug:slug>/unfollow', login_required(UnfollowView), name='unfollow'),
    path('podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>', EpisodeView, name='episode'),
    path('podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/edit', login_required(EditEpisodeView.as_view()), name='episode-edit'),
    path('profile', login_required(ProfileView.as_view()), name='profile'),
    path('profile/creator', login_required(CreatorView.as_view()), name='creator'),
    path('profile/become-creator', login_required(BecomeCreator), name='become-creator'),
    path('playlists/create', login_required(PlaylistCreateView.as_view()), name='playlist-create'),
    path('playlists/<int:playlist_id>', PlaylistView, name='playlist'),
    path('playlists/<int:playlist_id>/edit', login_required(PlaylistEditView.as_view()), name='playlist-edit'),
    path('playlists/<int:playlist_id>/delete', login_required(PlaylistDeleteView), name='playlist-delete'),
    path('playlists/<int:playlist_id>/remove/<int:episode_id>', login_required(DeleteEpisodeFromPlaylist), name='playlist-episode-remove'),
    path('search', Search, name='search'),
    path('feed', login_required(Feed), name='feed'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

