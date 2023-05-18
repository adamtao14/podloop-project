import json
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,View
from .models import Category,Podcast,Episode,EpisodeLike
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponse


User = get_user_model()

def home(request):
    return render(request, 'core/home.html')


class CategoryListView(ListView):
    model = Category
    template_name = "core/categories.html"
    queryset = Category.objects.order_by("name")
    context_object_name = "categories"
    
def CategoryDetailView(request,slug):
    template_name = "core/category.html"
    category = get_object_or_404(Category,slug=slug)
    podcasts = Category.objects.get(slug=slug).podcasts.all()
    paginator_controller = Paginator(podcasts, 5)
    if request.GET.get("page"):
       current_page = int(request.GET.get("page"))
    else:
        current_page = 1
        
    podcasts_list = []
    pagination = {}
    #se super il numero di pagine non devo restituire niente
    if int(current_page) <= paginator_controller.num_pages:
        current_page_podcasts = paginator_controller.page(current_page)
        
        #creazione contesto per il template
        
        for podcast in current_page_podcasts.object_list:
            owner = User.objects.get(id=podcast.owner_id)
            categories = Podcast.objects.get(name=podcast.name).categories.all()
            followers = str(Podcast.objects.get(name=podcast.name).followers.all().count())

            podcasts_list.append({
                "description":podcast.description[:100]+"...",
                "name":podcast.name,
                "podcast_thumbnail":podcast.podcast_thumbnail,
                "owner_username":owner.username,
                "slug":podcast.slug,
                "categories":categories,
                "followers":followers 
                })
        
        pagination["current_page"] = current_page
        pagination["page_controller"] = current_page_podcasts
        
    context={"podcasts": podcasts_list, "pagination":pagination, "category_name":category.name}
    
    
    
    return render(request, template_name, context=context)


def PodcastView(request,slug):
    template_name = "core/podcast.html"
    podcast = get_object_or_404(Podcast, slug=slug)

    owner = User.objects.get(id=podcast.owner_id)
    followers = str(Podcast.objects.get(name=podcast.name).followers.all().count())
    sort_by = request.GET.get("sort_by")

    if sort_by == "old_to_new":
        episodes = podcast.episodes.all().order_by('upload_date')
    else:
        episodes = podcast.episodes.all().order_by('-upload_date')
        sort_by = "new_to_old"
            
    is_owner = False
    is_following = False
    categories = Podcast.objects.get(name=podcast.name).categories.all()
    
    if request.user.is_authenticated:
        if request.user.id == podcast.owner_id:
            is_owner = True
        else:
            current_user = User.objects.get(id=request.user.id)
            if current_user.followed_podcasts.filter(name=podcast.name).exists():
                is_following = True
                
    context = {
        "podcast":podcast,
        "owner":owner,
        "followers":followers,
        "is_owner":is_owner,
        "is_following":is_following,
        "episodes":episodes,
        "categories":categories,
        "sort_by":sort_by
    }            
    return render(request, template_name, context=context)
                    
def FollowView(request,slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    user = User.objects.get(id=request.user.id)
    if user.followed_podcasts.filter(name=podcast.name).exists():
        return redirect('core:podcast',slug)
    else:
        user.followed_podcasts.add(podcast)
        return redirect('core:podcast',slug)

def UnfollowView(request,slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    user = User.objects.get(id=request.user.id)
    if user.followed_podcasts.filter(name=podcast.name).exists():
        user.followed_podcasts.remove(podcast)
        return redirect('core:podcast',slug)
    else:
        return redirect('core:podcast',slug)
    

def EpisodeView(request,podcast_slug,episode_slug):
    template_name="core/episode.html"
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    owner = User.objects.get(id=podcast.owner_id)
                
    context = {
        "podcast":podcast,
        "episode":episode,
        "owner":owner,
    }            
    return render(request, template_name, context=context)


###FUNZIONI PER LE CHIAMATE ASYNC###
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
        
    json_data = json.dumps(data)
    return  HttpResponse(json_data, content_type='application/json')

def ApiUnfollow(request,podcast_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    data = {}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if current_user.followed_podcasts.filter(name=podcast.name).exists():
            current_user.followed_podcasts.remove(podcast)
            data["is_following"] = False
            
    json_data = json.dumps(data)
    return  HttpResponse(json_data, content_type='application/json')

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

    json_data = json.dumps(data)
    return  HttpResponse(json_data, content_type='application/json')



def ApiEpisodeLike(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    data = {}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if not EpisodeLike.objects.filter(user=current_user,episode=episode).exists():
            new_episode_like = EpisodeLike()
            new_episode_like.user = current_user
            new_episode_like.episode = episode
            new_episode_like.save()
            data["is_liked"] = True
    
    json_data = json.dumps(data)
    return  HttpResponse(json_data, content_type='application/json')
        
def ApiEpisodeDislike(request,podcast_slug,episode_slug):
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    data = {}
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if EpisodeLike.objects.filter(user=current_user,episode=episode).exists():
            EpisodeLike.objects.filter(user=current_user,episode=episode).delete()
            data["is_liked"] = False
    
    json_data = json.dumps(data)
    return  HttpResponse(json_data, content_type='application/json')