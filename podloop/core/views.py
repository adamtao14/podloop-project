from django.http import HttpResponse
from django.utils.text import slugify
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,View
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from accounts.models import EmailVerification
from accounts.utils import Util
from .forms import ProfileForm,PodcastForm,EpisodeForm,EpisodeEditForm,PlaylistForm
from .models import Category,Podcast,Episode,Playlist
from .validators import validate_audio_file
from urllib.parse import urlencode
import uuid


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
        episodes = podcast.episodes.filter(is_private=False).order_by('upload_date')
    else:
        episodes = podcast.episodes.filter(is_private=False).order_by('-upload_date')
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
    playlists = None
    show_episode = True
    
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        playlists = Playlist.objects.filter(owner=current_user)
        
        if episode.is_private:
            if podcast.owner.id == current_user.id:
                show_episode = True
            else:
                show_episode = False
        else:
            show_episode = True
    else:
        if episode.is_private:
            show_episode = False
        else:
            show_episode = True       

    if show_episode:
        context = {
            "podcast":podcast,
            "episode":episode,
            "owner":owner,
            "playlists":playlists,
        }            
        return render(request, template_name, context=context) 
    else:
        return HttpResponse(status=404)
        
                  


class ProfileView(View):
    template_name="core/profile.html" 
    form_class = ProfileForm
    def get(self, request):
        if request.user.is_authenticated:
            current_user = User.objects.get(id=request.user.id)
            playlists = Playlist.objects.filter(owner=current_user)
            form = self.form_class(initial={
                'email': current_user.email,
                'name': current_user.name,
                'last_name': current_user.last_name,
                'username': current_user.username,
            })
            
            success_email_change = request.GET.get('success_email_change')
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_email_change':success_email_change, 'playlists':playlists})
    
    def post(self, request):
        message = []
        current_user = User.objects.get(id=request.user.id)
        form = self.form_class(request.POST,request.FILES)
        playlists = Playlist.objects.filter(owner=current_user)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            last_name = form.cleaned_data.get("last_name")
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            link_profile_picture = form.cleaned_data.get("link_profile_picture")

            if name == current_user.name and last_name == current_user.last_name and username == current_user.username and email == current_user.email and not link_profile_picture :
                message = "No changes made"
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'playlists':playlists})
            else:
                if User.objects.filter(username=username).exists() and current_user.username != username:
                    message.append("Username already exists")
                if User.objects.filter(email=email).exists() and current_user.email != email:
                    message.append("Email already exists")    
                
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'playlists':playlists})

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
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'playlists':playlists})
        else:
            message.append("Invalid data")
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'playlists':playlists})



def BecomeCreator(request):
    template_name="core/become_creator.html"
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if current_user.is_creator:
            return redirect(reverse('core:creator'))
        else:
            if current_user.is_email_verified:
                return render(request, template_name, context={'user':current_user})   
            else:
            #if the user is not verified we send him an email to verify it
            #first we check id he already has a link to verify it in the db,if so we delete it and make a new one
                if EmailVerification.objects.filter(user_id=current_user).exists():
                    EmailVerification.objects.filter(user_id=current_user).delete()
                
                verify_code = uuid.uuid1()
                new_email_verification = EmailVerification(user=current_user,code=verify_code)
                new_email_verification.save()
                
                Util.send_creator_email(current_user.email,verify_code)
                message = "To become a creator you need to verify your email first, we sent you a link to do it in your email"
                return render(request, template_name, context={'user':current_user,'is_not_verified':message})

class CreatorView(View):
    template_name = 'core/creator_page.html'
    form_class = PodcastForm
    def get(self, request):
        current_user = User.objects.get(id=request.user.id)
        if current_user.is_email_verified:
            if not current_user.is_creator:
                #the first time the user gets to this page after confirming the email, we can set him as a creator
                current_user.is_creator = True
                current_user.save()
            show_delete_success = None
            
            if request.GET.get("delete_success"):
                show_delete_success = request.GET.get("delete_success")
            
            list_categories = Category.objects.values_list('name', flat=True)
            choices = [(value, value) for value in list_categories]
            form = self.form_class(choices=choices)
            user_podcasts = Podcast.objects.filter(owner=current_user)
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcasts':user_podcasts,'show_delete_success':show_delete_success})
        else:
            return redirect(reverse('core:become-creator'))
        
    def post(self, request):
        message = []
        current_user = User.objects.get(id=request.user.id)
        list_categories = Category.objects.values_list('name', flat=True)
        choices = [(value, value) for value in list_categories]
        form = self.form_class(choices,request.POST,request.FILES)
        user_podcasts = Podcast.objects.filter(owner=current_user)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            description = form.cleaned_data.get("description")
            categories = form.cleaned_data.get("categories")
            podcast_picture = form.cleaned_data.get("podcast_thumbnail")
            
            if Podcast.objects.filter(name=name).exists():
                message.append("A podcast with this name already exists")
            if message != []:
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcasts':user_podcasts})
            
            new_podcast = Podcast()
            new_podcast.name = name
            new_podcast.slug = slugify(name)
            new_podcast.description = description
            new_podcast.owner = current_user
            new_podcast.podcast_thumbnail = podcast_picture
            new_podcast.save()
            for category in categories:
                chosen_category = Category.objects.get(name=category)
                new_podcast.categories.add(chosen_category)
            new_podcast.save()
            #empty form
            form = self.form_class(choices)

            
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcasts':user_podcasts})
            
        else:
            message.append("Invalid data")
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcasts':user_podcasts})


class PodcastEditView(View):
    template_name = 'core/edit_podcast.html'
    form_class = PodcastForm
    def get(self,request,slug):
        current_user = User.objects.get(id=request.user.id)
        podcast = get_object_or_404(Podcast,slug=slug)
        episodes = podcast.episodes.all()
        if current_user == podcast.owner:
            list_categories = Category.objects.values_list('name', flat=True)
            choices = [(value, value) for value in list_categories]
            preselected_choices = [value for value in podcast.categories.all()]
            show_delete_success = None
            if request.GET.get("delete_success"):
                show_delete_success = request.GET.get("delete_success")
            form = self.form_class(choices=choices,initial={
                'name': podcast.name,
                'description': podcast.description,
                'categories': preselected_choices,
            })
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcast':podcast, 'episodes':episodes, 'show_delete_success':show_delete_success})
        else:
            return HttpResponse(status=401)
        
    def post(self,request,slug):
        message = []
        current_user = User.objects.get(id=request.user.id)
        list_categories = Category.objects.values_list('name', flat=True)
        choices = [(value, value) for value in list_categories]
        form = self.form_class(choices,request.POST,request.FILES)
        podcast = get_object_or_404(Podcast,slug=slug)
        episodes = podcast.episodes.all()
        preselected_choices = [value for value in podcast.categories.all().values_list('name',flat=True)]
        if current_user.id == podcast.owner.id:
            if form.is_valid():
                
                
                name = form.cleaned_data.get("name")
                description = form.cleaned_data.get("description")
                categories = form.cleaned_data.get("categories")
                podcast_thumbnail = form.cleaned_data.get("podcast_thumbnail")

                if name==podcast.name and description == podcast.description and set(preselected_choices) == set(categories) and not podcast_thumbnail:
                    message = "No changes made"
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'podcast':podcast, 'episodes':episodes})
                    
                if name != podcast.name:
                    if Podcast.objects.filter(name=name).exists():
                        message.append("A podcast with this name already exists")
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast, 'episodes':episodes})
                
                podcast.name = name
                podcast.slug = slugify(name)
                podcast.description = description
                if podcast_thumbnail:
                    podcast.podcast_thumbnail = podcast_thumbnail
                podcast.save()
                podcast.categories.clear()
                for category in categories:
                    chosen_category = Category.objects.get(name=category)
                    podcast.categories.add(chosen_category)
                podcast.save()
                #empty form
                preselected_choices = [value for value in podcast.categories.all().values_list('name',flat=True)]
                form = self.form_class(choices=choices,initial={
                    'name': podcast.name,
                    'description': podcast.description,
                    'categories': preselected_choices,
                })

                
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcast':podcast, 'episodes':episodes})
                
            else:
                message.append("Invalid data")
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast, 'episodes':episodes})
        else:
            return HttpResponse(statu=401)

class PodcastEpisodeUpload(View):
    template_name = 'core/upload_episode.html'
    form_class = EpisodeForm
    def get(self,request,slug):
        podcast = Podcast.objects.get(slug=slug)
        current_user = User.objects.get(id=request.user.id)
        if podcast.owner.id == current_user.id:
            form = self.form_class()
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcast':podcast})
        else:
            return HttpResponse(status=404)
        
    
    def post(self,request,slug):
        podcast = Podcast.objects.get(slug=slug)
        current_user = User.objects.get(id=request.user.id)
        message = []
        if podcast.owner.id == current_user.id:
            form = self.form_class(request.POST,request.FILES)
            if form.is_valid():
                title = form.cleaned_data.get("title")
                description = form.cleaned_data.get("description")
                audio = form.cleaned_data.get("audio")
                episode_thumbnail = form.cleaned_data.get("episode_thumbnail")
                is_private = form.cleaned_data.get("is_private")
                length = form.cleaned_data.get("length")
                
                try: 
                    validate_audio_file(audio)
                except ValidationError:
                    message.append("Audio must be of format [MP3, WAV, OGG] and size less than 250MB")
                
                if Episode.objects.filter(title=title).exists():
                    message.append("Title already exists for this podcast")
                  
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast})
                
                new_episode = Episode()
                new_episode.podcast = podcast
                new_episode.title = title
                new_episode.slug = slugify(title)
                new_episode.description = description
                new_episode.is_private = is_private
                new_episode.episode_thumbnail = episode_thumbnail
                new_episode.audio = audio
                new_episode.length = length
                new_episode.save()
                form = self.form_class()
                message = "Episode uploaded successfully"
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'podcast':podcast})
            else:
                message.append("Invalid data")
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast})
        else:
            return HttpResponse(status=404)
                
class EditEpisodeView(View):
    template_name = "core/edit_episode.html"
    form_class = EpisodeEditForm
    
    def get(self,request,podcast_slug,episode_slug):
        podcast = Podcast.objects.get(slug=podcast_slug)
        episode = Episode.objects.get(podcast=podcast,slug=episode_slug)
        current_user = User.objects.get(id=request.user.id)
        if podcast.owner.id == current_user.id:
            form = self.form_class(initial={
                'title':episode.title,
                'description':episode.description,
                'is_private':episode.is_private
            })
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcast':podcast, 'episode':episode})
        else:
            return HttpResponse(status=401)
        
    
    def post(self,request,podcast_slug,episode_slug):
        podcast = Podcast.objects.get(slug=podcast_slug)
        episode = Episode.objects.get(podcast=podcast,slug=episode_slug)
        current_user = User.objects.get(id=request.user.id)
        message = []
        if podcast.owner.id == current_user.id:
            form = self.form_class(request.POST,request.FILES)
            if form.is_valid():
                title = form.cleaned_data.get("title")
                description = form.cleaned_data.get("description")
                episode_thumbnail = form.cleaned_data.get("episode_thumbnail")
                is_private = form.cleaned_data.get("is_private")
                
                if title == episode.title and description == episode.description and is_private == episode.is_private and not episode_thumbnail:
                    message = "No changes were made"
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'podcast':podcast, 'episode':episode})
                
                if episode.title != title:
                    if Episode.objects.filter(title=title).exists():
                        message.append("Title already exists for this podcast")
                        
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast, 'episode':episode})
                
                episode.title = title
                episode.slug = slugify(title)
                episode.description = description
                episode.is_private = is_private
                if episode_thumbnail:
                    episode.episode_thumbnail = episode_thumbnail
                episode.save()
                form = self.form_class()
                message = "Episode edited successfully"
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'podcast':podcast, 'episode':episode})
            else:
                message.append("Invalid data")
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast, 'episode':episode})
        else:
            return HttpResponse(status=401)
        
def PlaylistView(request,playlist_id):
    template_name="core/playlist.html"
    playlist = get_object_or_404(Playlist, id=playlist_id)
    owner = User.objects.get(id=playlist.owner.id)
    episodes = playlist.episodes.all()
    show_playlist = True
    is_owner = False
    #show the playlist if not private to veryone,if private only to owner
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if current_user.id == playlist.owner.id:
            is_owner = True
        if playlist.is_private and is_owner:
            show_playlist = True
        elif playlist.is_private:
            show_playlist = False
    else:
        if playlist.is_private:
            show_playlist = False
        else:
            show_playlist = True

    if show_playlist:
        return render(request, template_name, context={'playlist':playlist, 'is_owner':is_owner, 'owner':owner, 'episodes':episodes})
    else:
        return HttpResponse(status=401)

def DeleteEpisodeFromPlaylist(request,playlist_id,episode_id):
    current_user = User.objects.get(id=request.user.id)
    playlist = get_object_or_404(Playlist,id=playlist_id)
    episode_id = get_object_or_404(Episode,id=episode_id)
    
    if playlist.owner.id == current_user.id:
        playlist.episodes.remove(episode_id)
        return redirect(reverse('core:playlist', kwargs={'playlist_id': playlist_id}))
    else:
        return HttpResponse(status=401)


class PlaylistCreateView(View):
    template_name = "core/create_playlist.html"
    form_class = PlaylistForm
    
    def get(self,request):
        form = self.form_class()
        current_user = User.objects.get(id=request.user.id)
        return render(request, self.template_name, context={'form': form, 'user':current_user})
        
    def post(self,request):
        if request.user.is_authenticated:    
            message = []
            form = self.form_class(request.POST)
            current_user = User.objects.get(id=request.user.id)
            if form.is_valid():
                name = form.cleaned_data.get("name")
                description = form.cleaned_data.get("description")
                is_private = form.cleaned_data.get("is_private")
                Playlist.objects.create(name=name,description=description,is_private=is_private,owner=current_user)
                message = "Playlist created"
                return render(request, self.template_name, context={'user':current_user, 'form':form, 'success_message':message})
            else:
                message.append("Invalid data")
                return render(request, self.template_name, context={'user':current_user, 'form':form, 'error_message':message})
        else:
            return HttpResponse(status=401)

class PlaylistEditView(View):
    template_name = "core/create_playlist.html"
    form_class = PlaylistForm
    
    def get(self,request,playlist_id):
        current_user = User.objects.get(id=request.user.id)
        playlist = get_object_or_404(Playlist,id=playlist_id)
        if current_user.id == playlist.owner.id:
            form = self.form_class(initial={
                'name': playlist.name,
                'description': playlist.description,
                'is_private': playlist.is_private,
            })    
            
            return render(request, self.template_name, context={'form': form, 'user':current_user})
        else:
            return HttpResponse(status=401)
        
    def post(self,request,playlist_id):
        if request.user.is_authenticated:    
            message = []
            form = self.form_class(request.POST)
            current_user = User.objects.get(id=request.user.id)
            playlist = get_object_or_404(Playlist,id=playlist_id)
            if form.is_valid():
                name = form.cleaned_data.get("name")
                description = form.cleaned_data.get("description")
                is_private = form.cleaned_data.get("is_private")
                playlist.name = name
                playlist.description = description
                playlist.is_private = is_private
                playlist.save()
                message = "Playlist updated successfully"
                return render(request, self.template_name, context={'user':current_user, 'form':form, 'success_message':message})
            else:
                message.append("Invalid data")
                return render(request, self.template_name, context={'user':current_user, 'form':form, 'error_message':message})
        else:
            return HttpResponse(status=401)       