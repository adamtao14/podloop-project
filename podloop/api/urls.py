from django.conf import settings
from django.urls import path
from .views import ApiIsAuth,ApiGetEpisodeUserInfo,ApiPostComment,ApiGetComments,ApiToggleLikeComment,ApiDeleteComment,ApiToggleLikeEpisode,ApiToggleFollow,ApiDeletePodcast,ApiDeleteEpisode,ApiAddEpisodeToPlaylist,ApiStreamEpisode,ApiDeleteAccount
from django.conf.urls.static import static
app_name = "api"

urlpatterns = [
    path('api/is-authenticated', ApiIsAuth),
    path('api/delete-account', ApiDeleteAccount, name="delete-account"),
    path('api/comment/<int:comment_id>/toggle-like', ApiToggleLikeComment),
    path('api/comment/<int:comment_id>/delete', ApiDeleteComment),
    path('api/podcasts/<slug:podcast_slug>/delete', ApiDeletePodcast),
    path('api/podcasts/<slug:podcast_slug>/toggle-follow', ApiToggleFollow),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>', ApiGetEpisodeUserInfo),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/post-comment', ApiPostComment),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/get-comments', ApiGetComments),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/toggle-like', ApiToggleLikeEpisode),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/delete', ApiDeleteEpisode),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/add-to-playlist/<int:playlist_id>', ApiAddEpisodeToPlaylist),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/stream', ApiStreamEpisode),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)