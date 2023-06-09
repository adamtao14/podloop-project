from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category) 
admin.site.register(Podcast) 
admin.site.register(Episode) 
admin.site.register(Playlist) 
admin.site.register(EpisodeLike) 
admin.site.register(EpisodeStream) 
admin.site.register(EpisodeComment) 
admin.site.register(EpisodeCommentLike) 
admin.site.register(PodcastFollow) 



