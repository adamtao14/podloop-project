from django.contrib.auth import get_user_model
from core.models import Podcast,EpisodeLike,Episode,EpisodeComment,EpisodeCommentLike
from django.utils.html import escape
User = get_user_model()

###FUNZIONI PER LE CHIAMATE ASYNC###
import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404



def ApiIsAuth(request):
    data = {"is_authenticated":request.user.is_authenticated}
    json_data = json.dumps(data)
    return  HttpResponse(json_data, content_type='application/json')

def ApiFollow(request,podcast_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    current_user = User.objects.get(id=request.user.id)
    data = {}
    if request.user.is_authenticated:
        if not current_user.followed_podcasts.filter(name=podcast.name).exists():
            current_user.followed_podcasts.add(podcast)
            data["is_following"] = True
            return HttpResponse(json.dumps(data), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps(data), content_type='application/json',status=401)
    

def ApiUnfollow(request,podcast_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    data = {}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if current_user.followed_podcasts.filter(name=podcast.name).exists():
            current_user.followed_podcasts.remove(podcast)
            data["is_following"] = False
            return HttpResponse(json.dumps(data), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps(data), content_type='application/json',status=401)       
   

def ApiToggleFollow(request,podcast_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    data = {}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if current_user.followed_podcasts.filter(name=podcast.name).exists():
            current_user.followed_podcasts.remove(podcast)
            data["is_following"] = False
            return HttpResponse(json.dumps(data), content_type='application/json', status=200)
        else:
            current_user.followed_podcasts.add(podcast)
            data["is_following"] = True
            return HttpResponse(json.dumps(data), content_type='application/json', status=200)  
    else:
        return HttpResponse(json.dumps(data), content_type='application/json',status=401)

def ApiGetEpisodeUserInfo(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    followers = str(Podcast.objects.get(name=podcast.name).followers.all().count())
    likes = EpisodeLike.objects.filter(episode=episode).all().count()
    is_owner = False
    is_following = False
    is_liked = False
    
    if request.user.is_authenticated:
        if EpisodeLike.objects.filter(episode=episode,user=request.user.id).exists():
            is_liked = True
        if request.user.id == podcast.owner_id:
            is_owner = True
        else:
            current_user = User.objects.get(id=request.user.id)
            if current_user.followed_podcasts.filter(name=podcast.name).exists():
                is_following = True
    
    
    data = {
        'followers':followers,
        'likes':likes,
        'is_owner':is_owner,
        'is_following':is_following,
        'is_liked':is_liked,
    }

    return  HttpResponse(json.dumps(data), content_type='application/json', status=200)


def ApiPostComment(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    data = {}
    if request.method == "POST":
        data_post = json.loads(request.body.decode('utf-8'))
        print(data_post)
        comment = escape(data_post.get('comment'))
        is_reply = data_post.get('is_reply')
        
        if request.user.is_authenticated:
            current_user = User.objects.get(id=request.user.id)
            new_comment = EpisodeComment()
            new_comment.owner = current_user
            new_comment.episode = episode
            new_comment.text = comment
            if is_reply:
                parent_comment = EpisodeComment.objects.get(id=data_post.get("reply_to"))
                new_comment.parent_comment = parent_comment
            new_comment.save()
            return HttpResponse(json.dumps(data),content_type='application/json', status=200)
        else:   
            return HttpResponse(json.dumps(data),content_type='application/json', status=401)
    else:
        return HttpResponse(json.dumps(data),content_type='application/json', status=400)
    

def ApiGetComments(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    data = {}
    data["sort_by"] = "old_to_new"
    if request.user.is_authenticated:
        data["comments"] = []
        current_user = User.objects.get(id=request.user.id)
        if request.GET.get("sort_by") == "new_to_old":
            comments = EpisodeComment.objects.filter(episode=episode).all().order_by("-date")
            data["sort_by"] = "new_to_old"
        else:
            comments = EpisodeComment.objects.filter(episode=episode).all().order_by("date")
        for comment in comments:
            #for each comment in the episode i only take the ones that are not replies
            if not comment.parent_comment:
                
                comment_data = {}
                is_owner = comment.owner.id == request.user.id
                is_liked = EpisodeCommentLike.objects.filter(user=current_user,comment=comment).exists()
                comment_likes = EpisodeCommentLike.objects.filter(comment=comment).all().count()
                if comment.owner.link_profile_picture:
                    link_profile_picture = comment.owner.link_profile_picture.url
                else:
                    link_profile_picture = '/media/images/default_podcast_thumbnail.jpg'
                  
                comment_data["comment"] = {"id":comment.id,"text":comment.text,"date":str(comment.date.strftime('%Y-%m-%d %H:%M')),"owner":comment.owner.username,"is_owner":is_owner, "link_profile_picture":link_profile_picture,"is_liked":is_liked,"likes":comment_likes}
                
                #i get all the replies of this comment
                comment_replies = EpisodeComment.objects.filter(episode=episode,parent_comment=comment).all().order_by("date")
                #if the comment is not a reply then it's a parent comment, now i get all the replies of the comment
                comment_data["replies"] = []
                for comment_reply in comment_replies:
                    is_owner = comment_reply.owner.id == request.user.id
                    is_liked = EpisodeCommentLike.objects.filter(user=current_user,comment=comment_reply).exists()
                    comment_likes = EpisodeCommentLike.objects.filter(comment=comment_reply).all().count()
                    if comment_reply.owner.link_profile_picture:
                        link_profile_picture = comment_reply.owner.link_profile_picture.url
                    else:
                        link_profile_picture = '/media/images/default_podcast_thumbnail.jpg'
                    comment_data["replies"].append({"id":comment_reply.id,"text":comment_reply.text,"date":str(comment_reply.date.strftime('%Y-%m-%d %H:%M')),"owner":comment_reply.owner.username,"is_owner":is_owner,"link_profile_picture":link_profile_picture,"is_liked":is_liked,"likes":comment_likes})
                data["comments"].append(comment_data)
        return HttpResponse(json.dumps(data), content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps(data), content_type='application/json', status=401)
    
def ApiToggleLikeEpisode(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    data = {}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if EpisodeLike.objects.filter(user=current_user,episode=episode).exists():
            EpisodeLike.objects.filter(user=current_user,episode=episode).delete()
            data["is_liked"] = False
            return HttpResponse(json.dumps(data),content_type='application/json', status=200)
        else:
            new_episode_like = EpisodeLike()
            new_episode_like.user = current_user
            new_episode_like.episode = episode
            new_episode_like.save()
            data["is_liked"] = True
            return HttpResponse(json.dumps(data),content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps(data),content_type='application/json',status=401)
    
    
def ApiToggleLikeComment(request,comment_id):
    data = {}
    if request.user.is_authenticated:
        comment = get_object_or_404(EpisodeComment, id=comment_id)
        current_user = User.objects.get(id=request.user.id)
        if EpisodeCommentLike.objects.filter(comment=comment,user=current_user).exists():
            #if the user already liked the comment then i remove the like
            EpisodeCommentLike.objects.get(comment=comment,user=current_user).delete()
        else:
            #if the user hasn't liked the comment then i add the like
            EpisodeCommentLike.objects.create(user=current_user,comment=comment)
        return HttpResponse(json.dumps(data),content_type='application/json', status=200)
    else:
        return HttpResponse(json.dumps(data),content_type='application/json', status=401)
    
    
def ApiDeleteComment(request,comment_id):
    data = {}
    if request.user.is_authenticated:
        comment = get_object_or_404(EpisodeComment, id=comment_id)
        if comment.owner.id == request.user.id:
            comment.delete()
            return HttpResponse(json.dumps(data),content_type='application/json', status=200)
        else:
            return HttpResponse(json.dumps(data),content_type='application/json', status=401)
    else:
        return HttpResponse(json.dumps(data),content_type='application/json', status=401)        
        
def ApiDeletePodcast(request,podcast_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if podcast.owner.id == current_user.id:
            podcast.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponse(status=401)
    
def ApiDeleteEpisode(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if episode.podcast.owner.id == current_user.id:
            episode.delete()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=401)
    else:
        return HttpResponse(status=401)