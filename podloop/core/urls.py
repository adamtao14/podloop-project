from django.urls import path
from .views import Home,CategoryListView,CategoryDetailView,PodcastView,FollowPodcast,UnfollowPodcast,EpisodeView,ProfileView,CreatorView,BecomeCreator,PodcastEditView,PodcastEpisodeUpload,EditEpisodeView,PlaylistCreateView,PlaylistEditView,PlaylistView,DeleteEpisodeFromPlaylist,PlaylistDeleteView,Search,Feed,PodcastAnalytics,HomePage
from .utils import load_data
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
app_name = "core"

# load database's initial data
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

