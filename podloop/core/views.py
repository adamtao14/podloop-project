import json
from urllib.parse import urlencode
import uuid
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,View,UpdateView
from django.urls import reverse
from accounts.models import EmailVerification
from accounts.utils import Util
from .models import Category,Podcast,Episode
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from accounts.forms import ProfileForm


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


class ProfileView(View):
    template_name="core/profile.html" 
    form_class = ProfileForm
    def get(self, request):
        if request.user.is_authenticated:
            
            
            current_user = User.objects.get(id=request.user.id)
            form = self.form_class(initial={
                'email': current_user.email,
                'name': current_user.name,
                'last_name': current_user.last_name,
                'username': current_user.username,
            })
            
            success_email_change = request.GET.get('success_email_change')
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_email_change':success_email_change})
    
    def post(self, request):
        message = []
        current_user = User.objects.get(id=request.user.id)
        form = self.form_class(request.POST,request.FILES)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            last_name = form.cleaned_data.get("last_name")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            link_profile_picture = form.cleaned_data.get("link_profile_picture")
            print("pp:",link_profile_picture)
            if name == current_user.name and last_name == current_user.last_name and username == current_user.username and email == current_user.email and not link_profile_picture :
                message = "No changes made"
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message})
            else:
                if User.objects.filter(username=username).exists() and current_user.username != username:
                    message.append("Username already exists")
                if User.objects.filter(email=email).exists() and current_user.email != email:
                    message.append("Email already exists")    
                
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message})

                current_user.name = name
                current_user.last_name = last_name
                current_user.username = username
                if link_profile_picture:
                    current_user.link_profile_picture = link_profile_picture

                if current_user.email != email:
                    current_user.email = email
                    current_user.is_email_verified = False
                    current_user.save()
                    
                    verify_code = uuid.uuid1()
                    new_email_verification = EmailVerification(user=current_user,code=verify_code)
                    new_email_verification.save()
                    
                    Util.send_confirm_email(email,verify_code)
                
                    
                    message = "Your email has been updated, please verify it at the link we sent you"
                    url = reverse('core:profile')+ '?' + urlencode({'success_email_change': message})
                    return redirect(url)
                else:
                    current_user.save()
                    message = "Updated successfully"
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message})
        else:
            message.append("Invalid data")
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message})


