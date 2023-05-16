from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView,View
from .models import Category,Podcast,Episode
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

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
    episodes = podcast.episodes.all()
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
        "categories":categories
    }            
    return render(request, template_name, context=context)
                    
