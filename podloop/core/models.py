from django.db import models
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .validators import validate_audio_file,validate_image_file

## USER MODELS ##
User = get_user_model()


## PODCAST MODELS ##
        
class Category(models.Model):
    name = models.CharField(max_length=50,unique=True,blank=False)
    description = models.CharField(max_length=100,null=True,default=None,blank=True)
    slug = models.CharField(max_length=100,unique=True,null=True)
    class Meta:
        verbose_name_plural = "Categories"
  
    def __str__(self):
        return self.name

class Podcast(models.Model):
    name = models.CharField(max_length=300,blank=False, unique=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,blank=False)
    slug = models.CharField(max_length=500,unique=True,null=True)
    #followers = models.ManyToManyField(User,related_name="followed_podcasts",symmetrical=False)
    description = models.CharField(max_length=500,blank=False)
    categories = models.ManyToManyField(Category,related_name="podcasts",symmetrical=False,blank=False)
    podcast_thumbnail = models.FileField(upload_to='images/',blank=True, validators=[validate_image_file])
    
    class Meta:
        verbose_name_plural = "Podcasts"
    
    def __str__(self):
        return self.name

class PodcastFollow(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    podcast = models.ForeignKey(Podcast,on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['user', 'podcast'], name='id_follow'
                )
            ]
        verbose_name_plural = "PodcastFollows"
    
    def __str__(self):
        return self.user.username + " follows " + self.podcast.name
    
class Episode(models.Model):
    title = models.CharField(max_length=200,blank=False)
    description = models.CharField(max_length=500,blank=False)
    upload_date = models.DateTimeField(default=now)
    audio = models.FileField(upload_to='audios/',blank=False, validators=[validate_audio_file])
    episode_thumbnail = models.FileField(upload_to='images/',blank=True, validators=[validate_image_file])
    podcast = models.ForeignKey(Podcast,on_delete=models.CASCADE,related_name="episodes")
    is_private = models.BooleanField(default=False,blank=False)
    length = models.CharField(max_length=30, blank=True)
    slug = models.CharField(max_length=500,null=True)
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['podcast', 'title'], name='id_episode'
                )
            ]
        verbose_name_plural = "Episodes"
    
    def __str__(self):
        return self.title    
class Playlist(models.Model):
    name = models.CharField(max_length=100,blank=False)
    is_private = models.BooleanField(default=False,blank=False)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    description = models.CharField(max_length=200,blank=True)
    episodes = models.ManyToManyField(Episode,symmetrical=False)
    date = models.DateTimeField(default=now)
    
    class Meta:
        verbose_name_plural = "Playlists"
    
    def __str__(self):
        return self.name
    
class EpisodeLike(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode,on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['user', 'episode'], name='id_like'
                )
            ]
        verbose_name_plural = "EpisodeLikes"
        
    def __str__(self):
        return self.user.username + " liked " + self.episode.title
    
class EpisodeStream(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode,on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['user', 'episode', 'date'], name='id_stream'
                )
            ]
        verbose_name_plural = "EpisodeStreams"
        
    def __str__(self):
        return self.user.username + " streamed " + self.episode.title

class EpisodeComment(models.Model):
    episode = models.ForeignKey(Episode,on_delete=models.CASCADE,related_name="comments")
    text = models.CharField(max_length=500, blank=False)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self',on_delete=models.CASCADE,null=True,default=None)
    date = models.DateTimeField(default=now)
    
    class Meta:
        verbose_name_plural = "EpisodeComments"
    
    def __str__(self):
        return self.owner.username + " commented on " + self.episode.title
    
class EpisodeCommentLike(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="my_comment_likes")
    comment = models.ForeignKey(EpisodeComment,on_delete=models.CASCADE)
    date = models.DateTimeField(default=now)
    
    class Meta:
        constraints = [
                models.UniqueConstraint(
                    fields=['user', 'comment'], name='id_comment_like'
                )
            ]
        
        verbose_name_plural = "EpisodeCommentLikes"
    
    def __str__(self):
        return self.user.username + " liked a comment"
