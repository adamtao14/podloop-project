from django.conf import settings
from django.urls import path
from .views import ApiFollow,ApiUnfollow,ApiIsAuth,ApiGetEpisodeUserInfo,ApiPostComment,ApiGetComments,ApiToggleLikeComment,ApiDeleteComment,ApiToggleLikeEpisode,ApiToggleFollow
from django.conf.urls.static import static
app_name = "api"

urlpatterns = [
    path('api/podcasts/<slug:podcast_slug>/follow', ApiFollow),
    path('api/podcasts/<slug:podcast_slug>/unfollow', ApiUnfollow),
    path('api/podcasts/<slug:podcast_slug>/toggle-follow', ApiToggleFollow),
    path('api/is-authenticated', ApiIsAuth),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>', ApiGetEpisodeUserInfo),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/post-comment', ApiPostComment),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/get-comments', ApiGetComments),
    path('api/comment/<int:comment_id>/toggle-like', ApiToggleLikeComment),
    path('api/podcasts/<slug:podcast_slug>/episode/<slug:episode_slug>/toggle-like', ApiToggleLikeEpisode),
    path('api/comment/<int:comment_id>/delete', ApiDeleteComment),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)