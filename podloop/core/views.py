from datetime import timedelta
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.timezone import now
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView,View
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import Count,Q
from accounts.models import EmailVerification
from accounts.utils import Util
from .forms import ProfileForm,PodcastForm,EpisodeForm,EpisodeEditForm,PlaylistForm
from .models import Category,Podcast,Episode,Playlist,EpisodeStream,EpisodeLike,EpisodeComment,PodcastFollow
from .validators import validate_audio_file
from urllib.parse import urlencode
import uuid


User = get_user_model()

def HomePage(request):
    template_name = "core/homepage.html"
    return render(request,template_name,context={})
    
class Home(View):
    template_name = "core/home.html"
    current_user = None
    def get(self,request):
        recommended_podcasts = None
        if request.user.is_authenticated:
            self.current_user = User.objects.get(id=request.user.id)
            recommended_podcasts = self.collaborative_filtering()
        return render(request,self.template_name, context={'recommended_podcasts':recommended_podcasts})
    
    def collaborative_filtering(self):
       
        # Calculate Similarity between Users
        followed_podcasts = PodcastFollow.objects.filter(user=self.current_user).values_list('podcast_id', flat=True)
        streamed_episodes = EpisodeStream.objects.filter(user=self.current_user).values_list('episode__podcast_id', flat=True)
        
        common_podcasts = set(followed_podcasts).intersection(set(streamed_episodes))
        
        similar_users = PodcastFollow.objects.filter(podcast_id__in=common_podcasts).exclude(user=self.current_user)\
            .values('user').annotate(similarity=Count('podcast_id')).order_by('-similarity')[:10]
        
        # Recommend Podcasts
        recommended_podcasts = []
        
        for similar_user in similar_users:
            # Get podcasts followed by similar users
            similar_user_followed_podcasts = PodcastFollow.objects.filter(user=similar_user['user']).values_list('podcast_id', flat=True)
            
            # Exclude podcasts already followed by the target user
            recommended_podcasts.extend(list(set(similar_user_followed_podcasts) - set(followed_podcasts)))
        
        # Fetch recommended podcast details
        recommended_podcasts = Podcast.objects.filter(id__in=recommended_podcasts)
        
        if not recommended_podcasts:
        # Provide alternative recommendations in case of no recommended podcasts
            recommended_podcasts = Podcast.objects.exclude(id__in=followed_podcasts)[:10]
        
        return recommended_podcasts
        


class CategoryListView(ListView):
    # List all the categories
    model = Category
    template_name = "core/categories.html"
    queryset = Category.objects.order_by("name")
    context_object_name = "categories"
    
def CategoryDetailView(request,slug):
    template_name = "core/category.html"
    category = get_object_or_404(Category,slug=slug)
    if request.GET.get("page"):
        # Get current page if page parameter exists
       current_page = int(request.GET.get("page"))
    else:
        # If not present we are in the first page
        current_page = 1
    
    if request.GET.get("sort_by"):
        sort_by = request.GET.get("sort_by")
    else:
        sort_by = "name"
    
    results_before_pagination = None
     
    if sort_by == "name":
        results_before_pagination = Category.objects.get(slug=slug).podcasts.order_by("name")
    elif sort_by == "-name":
        results_before_pagination = Category.objects.get(slug=slug).podcasts.order_by("-name")
    elif sort_by == "most-followed":
        results_before_pagination = Category.objects.get(slug=slug).podcasts.annotate(follow_count=Count('podcastfollow')).order_by("-follow_count")
    elif sort_by == "least-followed":   
        results_before_pagination = Category.objects.get(slug=slug).podcasts.annotate(follow_count=Count('podcastfollow')).order_by("follow_count")
        
    paginator_controller = Paginator(results_before_pagination, 5)
    podcasts_list = []
    pagination = {}
    # Only show if the current page is less then the maximum pages
    if int(current_page) <= paginator_controller.num_pages:
        # Get all the podcasts for that specific page
        current_page_podcasts = paginator_controller.page(current_page)
        # Get all the data needed for each retrieved podcast
        for podcast in current_page_podcasts.object_list:
            # Get the followers count of the podcast
            followers = str(PodcastFollow.objects.filter(podcast=podcast).all().count())

            podcasts_list.append({
                "podcast":podcast,
                "followers":followers 
                })
        
        pagination["current_page"] = current_page
        pagination["page_controller"] = current_page_podcasts
        
    context={"podcasts": podcasts_list, "pagination":pagination, "category":category, "sort_by":sort_by}
    return render(request, template_name, context=context)


def PodcastView(request,slug):
    template_name = "core/podcast.html"
    podcast = get_object_or_404(Podcast, slug=slug)
    followers = str(PodcastFollow.objects.filter(podcast=podcast).all().count())
    sort_by = request.GET.get("sort_by")

    # Sort episodes base on what the user wants
    if sort_by == "old_to_new":
        episodes = podcast.episodes.filter(is_private=False).order_by('upload_date')
    else:
        episodes = podcast.episodes.filter(is_private=False).order_by('-upload_date')
        sort_by = "new_to_old"
            
    is_owner = False
    is_following = False
    
    # Chek if the user owns the podcast or if he follows it
    if request.user.is_authenticated:
        if request.user.id == podcast.owner_id:
            is_owner = True
        else:
            current_user = User.objects.get(id=request.user.id)
            if PodcastFollow.objects.filter(podcast=podcast,user=current_user).exists():
                is_following = True
                
    context = {
        "podcast":podcast,
        "followers":followers,
        "is_owner":is_owner,
        "is_following":is_following,
        "episodes":episodes,
        "sort_by":sort_by
    }            
    return render(request, template_name, context=context)
                    
def FollowPodcast(request,slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    user = User.objects.get(id=request.user.id)
    # If the user doesn't follow the podcast, add the follow
    if not PodcastFollow.objects.filter(podcast=podcast,user=user).exists():
        PodcastFollow.objects.create(podcast=podcast,user=user)
    return redirect('core:podcast',slug)

def UnfollowPodcast(request,slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    user = User.objects.get(id=request.user.id)
    # If the user follows the podcast, remove the follow
    if PodcastFollow.objects.filter(podcast=podcast,user=user).exists():
        PodcastFollow.objects.get(podcast=podcast,user=user).delete()
    return redirect('core:podcast',slug)
    

def EpisodeView(request,podcast_slug,episode_slug):
    template_name="core/episode.html"
    podcast = get_object_or_404(Podcast, slug=podcast_slug)
    episode = get_object_or_404(Episode, slug=episode_slug, podcast=podcast)
    playlists = None
    show_episode = True
    streams = EpisodeStream.objects.filter(episode=episode).all().count()
    
    # Check if the user is the owner of the episode's podcast
    # This way we can show the private episodes only if you are the owner
    # If not only show the public ones
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
            "playlists":playlists,
            "streams":streams
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
            # Populate the profile form with the current values, in case the user wants to change them
            form = self.form_class(initial={
                'email': current_user.email,
                'name': current_user.name,
                'last_name': current_user.last_name,
                'username': current_user.username,
            })
            # In case the user changed their email previously, we will have the success message to show him
            success_email_change = request.GET.get('success_email_change')
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_email_change':success_email_change, 'playlists':playlists})
    
def post(self, request):
    message = []
    current_user = User.objects.get(id=request.user.id)
    form = self.form_class(request.POST, request.FILES)
    playlists = Playlist.objects.filter(owner=current_user)
    if form.is_valid():
        # Get the form data
        name = form.cleaned_data.get("name")
        last_name = form.cleaned_data.get("last_name")
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        link_profile_picture = form.cleaned_data.get("link_profile_picture")

        # Check if any changes were made
        if (
            name == current_user.name
            and last_name == current_user.last_name
            and username == current_user.username
            and email == current_user.email
            and not link_profile_picture
        ):
            message = "No changes made"
            return render(
                request,
                self.template_name,
                context={
                    'form': form,
                    'user': current_user,
                    'success_message': message,
                    'playlists': playlists
                }
            )
        else:
            # Check if username or email already exist
            if (
                User.objects.filter(username=username).exists()
                and current_user.username != username
            ):
                message.append("Username already exists")
            if (
                User.objects.filter(email=email).exists()
                and current_user.email != email
            ):
                message.append("Email already exists")

            if message != []:
                # Display error message if username or email already exist
                return render(
                    request,
                    self.template_name,
                    context={
                        'form': form,
                        'user': current_user,
                        'error_message': message,
                        'playlists': playlists
                    }
                )

            # Update user information
            current_user.name = name
            current_user.last_name = last_name
            current_user.username = username
            if link_profile_picture:
                current_user.link_profile_picture = link_profile_picture

            if current_user.email != email:
                # Update user email and send verification email
                current_user.email = email
                current_user.is_email_verified = False
                current_user.save()

                verify_code = uuid.uuid1()
                new_email_verification = EmailVerification(
                    user=current_user,
                    code=verify_code
                )
                new_email_verification.save()

                Util.send_confirm_email(email, verify_code)

                message = "Your email has been updated, please verify it at the link we sent you"
                url = reverse('core:profile') + '?' + urlencode({'success_email_change': message})
                return redirect(url)
            else:
                # Save user information if no email change
                current_user.save()
                message = "Updated successfully"
                return render(
                    request,
                    self.template_name,
                    context={
                        'form': form,
                        'user': current_user,
                        'success_message': message,
                        'playlists': playlists
                    }
                )
    else:
        # Display error message for invalid form data
        message.append("Invalid data")
        return render(
            request,
            self.template_name,
            context={
                'form': form,
                'user': current_user,
                'error_message': message,
                'playlists': playlists
            }
        )




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
                # If the user is not verified we send him an email to verify it
                # First we check if he already has a link to verify it in the database,if so we delete it and make a new one
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
            # If we delete a podcast we get redirected to this page and we have to who the delete successfull message
            if request.GET.get("delete_success"):
                show_delete_success = request.GET.get("delete_success")
            # Show the form to create a podcast and get the user's podcasts if he has any
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
            # Get form data
            name = form.cleaned_data.get("name")
            description = form.cleaned_data.get("description")
            categories = form.cleaned_data.get("categories")
            podcast_picture = form.cleaned_data.get("podcast_thumbnail")
            # Check if a podcast with that name already exists
            if Podcast.objects.filter(name=name).exists():
                message.append("A podcast with this name already exists")
            if message != []:
                return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcasts':user_podcasts})
            
            # If there are no errors, create the podcast
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
            # Empty form
            form = self.form_class(choices)
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'podcasts':user_podcasts})
            
        else:
            message.append("Invalid data")
            return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcasts':user_podcasts})


class PodcastEditView(View):
    template_name = 'core/edit_podcast.html'
    form_class = PodcastForm
    
    def get(self, request, slug):
        # Retrieve current user and podcast
        current_user = User.objects.get(id=request.user.id)
        podcast = get_object_or_404(Podcast, slug=slug)
        episodes = podcast.episodes.all()
        
        if current_user == podcast.owner:
            # Prepare form choices and preselected choices
            list_categories = Category.objects.values_list('name', flat=True)
            choices = [(value, value) for value in list_categories]
            preselected_choices = [value for value in podcast.categories.all()]
            show_delete_success = None
            
            if request.GET.get("delete_success"):
                show_delete_success = request.GET.get("delete_success")
                
            # Populate the form with initial values
            form = self.form_class(choices=choices, initial={
                'name': podcast.name,
                'description': podcast.description,
                'categories': preselected_choices,
            })
            
            return render(request, self.template_name, context={
                'form': form,
                'user': current_user,
                'podcast': podcast,
                'episodes': episodes,
                'show_delete_success': show_delete_success
            })
        else:
            return HttpResponse(status=401)
        
    def post(self, request, slug):
        message = []
        current_user = User.objects.get(id=request.user.id)
        list_categories = Category.objects.values_list('name', flat=True)
        choices = [(value, value) for value in list_categories]
        form = self.form_class(choices, request.POST, request.FILES)
        podcast = get_object_or_404(Podcast, slug=slug)
        episodes = podcast.episodes.all()
        preselected_choices = [value for value in podcast.categories.all().values_list('name', flat=True)]
        
        if current_user.id == podcast.owner.id:
            if form.is_valid():
                # Get form data
                name = form.cleaned_data.get("name")
                description = form.cleaned_data.get("description")
                categories = form.cleaned_data.get("categories")
                podcast_thumbnail = form.cleaned_data.get("podcast_thumbnail")

                # Check if any changes were made
                if (
                    name == podcast.name
                    and description == podcast.description
                    and set(preselected_choices) == set(categories)
                    and not podcast_thumbnail
                ):
                    message = "No changes made"
                    return render(request, self.template_name, context={
                        'form': form,
                        'user': current_user,
                        'success_message': message,
                        'podcast': podcast,
                        'episodes': episodes
                    })

                # Check if the new podcast name already exists
                if name != podcast.name:
                    if Podcast.objects.filter(name=name).exists():
                        message.append("A podcast with this name already exists")
                        
                if message != []:
                    return render(request, self.template_name, context={
                        'form': form,
                        'user': current_user,
                        'error_message': message,
                        'podcast': podcast,
                        'episodes': episodes
                    })
                
                # Update podcast information
                podcast.name = name
                podcast.slug = slugify(name)
                podcast.description = description
                if podcast_thumbnail:
                    podcast.podcast_thumbnail = podcast_thumbnail
                podcast.save()
                
                # Update podcast categories
                podcast.categories.clear()
                for category in categories:
                    chosen_category = Category.objects.get(name=category)
                    podcast.categories.add(chosen_category)
                podcast.save()
                
                # Clear the form and display success message
                preselected_choices = [value for value in podcast.categories.all().values_list('name', flat=True)]
                form = self.form_class(choices=choices, initial={
                    'name': podcast.name,
                    'description': podcast.description,
                    'categories': preselected_choices,
                })
                message = "Podcast updated successfully!"
                return render(request, self.template_name, context={
                    'form': form,
                    'user': current_user,
                    'podcast': podcast,
                    'episodes': episodes,
                    'success_message': message
                })
            else:
                # If data is not valid, send error message
                message.append("Invalid data")
                return render(request, self.template_name, context={
                    'form': form,
                    'user': current_user,
                    'error_message': message,
                    'podcast': podcast,
                    'episodes': episodes
                })
        else:
            return HttpResponse(status=401)


class PodcastEpisodeUpload(View):
    template_name = 'core/upload_episode.html'
    form_class = EpisodeForm
    def get(self,request,slug):
        podcast = Podcast.objects.get(slug=slug)
        current_user = User.objects.get(id=request.user.id)
        if podcast.owner.id == current_user.id:
            # If user is owner of podcast, show form
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
            # Get form data
            if form.is_valid():
                title = form.cleaned_data.get("title")
                description = form.cleaned_data.get("description")
                audio = form.cleaned_data.get("audio")
                episode_thumbnail = form.cleaned_data.get("episode_thumbnail")
                is_private = form.cleaned_data.get("is_private")
                length = form.cleaned_data.get("length")
                
                # Validate the audio file
                try: 
                    validate_audio_file(audio)
                except ValidationError:
                    message.append("Audio must be of format [MP3, WAV, OGG] and size less than 250MB")
                # Check if title already exists for another episode of the podcast
                if Episode.objects.filter(title=title,podcast=podcast).exists():
                    message.append("Title already exists for this podcast")
                  
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast})
                # If not error create the episode
                Episode.objects.create(podcast=podcast,title=title,slug=slugify(title),description=description,is_private=is_private,episode_thumbnail=episode_thumbnail,audio=audio,length=length)
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
            # Display update form
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
                # Get form data
                title = form.cleaned_data.get("title")
                description = form.cleaned_data.get("description")
                episode_thumbnail = form.cleaned_data.get("episode_thumbnail")
                is_private = form.cleaned_data.get("is_private")
                
                # Check if any changes were made
                if title == episode.title and description == episode.description and is_private == episode.is_private and not episode_thumbnail:
                    message = "No changes were made"
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'success_message':message, 'podcast':podcast, 'episode':episode})
                # Check if title already exist in that podcast
                if episode.title != title:
                    if Episode.objects.filter(title=title, podcast=podcast).exists():
                        message.append("Title already exists for this podcast")
                        
                if message != []:
                    return render(request, self.template_name, context={'form': form, 'user':current_user, 'error_message':message, 'podcast':podcast, 'episode':episode})
                
                # If no errors found, update episode
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
    # Show the playlist if not private to everyone,if private only to owner
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
        # If the user is the owner, delete episode
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
                # Check if form is valid
                name = form.cleaned_data.get("name")
                description = form.cleaned_data.get("description")
                is_private = form.cleaned_data.get("is_private")
                # Create playlist
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
            # Get playlist info to edit
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
                # Get form data and update playlist
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
   
def PlaylistDeleteView(request,playlist_id):
    current_user = User.objects.get(id=request.user.id)
    playlist = get_object_or_404(Playlist,id=playlist_id)   
    if current_user.id == playlist.owner.id:
        # If user is owner, delete playlist
        playlist.delete()
        return redirect(reverse('core:profile'))
    else:
        return HttpResponse(status=401)
     
def Search(request):
    template_name = "core/search_results.html"
    # Check if it's a get request
    if request.method == "GET":
        where = request.GET.get("where")
        query = request.GET.get("query")
         
        results_for_podcast = False
        results_before_pagination = []
        
        if where and query:
            # Check if user chose a sort
            sort_by = "name"
            if request.GET.get("sort_by"):
                sort_by = request.GET.get("sort_by")
            
            # If the user chooses to search in podcasts
            if where == "podcasts":
                if sort_by == "name":
                    results_before_pagination = Podcast.objects.filter(name__icontains=query).order_by("name")
                elif sort_by == "-name":
                    results_before_pagination = Podcast.objects.filter(name__icontains=query).order_by("-name")
                elif sort_by == "most-followed":
                    results_before_pagination = Podcast.objects.filter(name__icontains=query).annotate(follow_count=Count('podcastfollow')).order_by("-follow_count")
                elif sort_by == "least-followed":   
                    results_before_pagination = Podcast.objects.filter(name__icontains=query).annotate(follow_count=Count('podcastfollow')).order_by("follow_count")
                results_for_podcast = True
            # If the user chooses to search in episodes    
            elif where == "episodes":
                if sort_by == "name":
                    results_before_pagination = Episode.objects.filter(title__icontains=query, is_private=False).order_by("title")
                elif sort_by == "-name":
                    results_before_pagination = Episode.objects.filter(title__icontains=query, is_private=False).order_by("-title")
                elif sort_by == "most-streamed":
                    results_before_pagination = Episode.objects.filter(title__icontains=query, is_private=False).annotate(streams=Count('episodestream')).order_by("-streams")
                elif sort_by == "least-streamed":   
                    results_before_pagination = Episode.objects.filter(title__icontains=query, is_private=False).annotate(streams=Count('episodestream')).order_by("streams")
                            
            # Paginate results in groups of 5 results
            paginator_controller = Paginator(results_before_pagination, 5)
            if request.GET.get("page"):
                current_page = int(request.GET.get("page"))
            else:
                current_page = 1
                
            results = []
            pagination = {}
            # If it the current_page is grater than the number of pages, i don't return anything
            if int(current_page) <= paginator_controller.num_pages:
                results_page_controller = paginator_controller.page(current_page)
                
                for result in results_page_controller.object_list:
                    # For each result if they are results of podcasts, find the followers count for each one
                   if results_for_podcast:
                        podcast_followers = PodcastFollow.objects.filter(podcast=result).all().count()
                        results.append({'podcast':result,'followers':podcast_followers})
                   else:
                        episode_streams = EpisodeStream.objects.filter(episode=result).all().count()
                        results.append({'episode':result,'streams':episode_streams})
                
                pagination["current_page"] = current_page
                pagination["page_controller"] = results_page_controller
                
        return render(request, template_name, context={'results':results, 'number_of_results':results_before_pagination.count(), 'pagination':pagination, 'where':where, 'query':query, 'results_for_podcast':results_for_podcast, 'sort_by':sort_by})
    else:
        return HttpResponse(status=401)       
                
                
def Feed(request):
    template_name = "core/feed.html"
    current_user = User.objects.get(id=request.user.id)
    one_day_ago = now() - timedelta(days=1)
    episodes_list = []
    followed_podcasts = PodcastFollow.objects.filter(user=current_user).values_list('podcast',flat=True)
    episodes = Episode.objects.filter(podcast__in=followed_podcasts, upload_date__gte=one_day_ago).order_by('-upload_date')
    # Get all the user's follows and the relative episodes uploaded in the last 24 hours
    for episode in episodes:
        streams = 0
        if EpisodeStream.objects.filter(episode=episode).exists():
            # For each episode get the streams count
            streams = EpisodeStream.objects.filter(episode=episode).all().count()
        episodes_list.append({'episode':episode,'streams':streams})
    followings = PodcastFollow.objects.filter(user=current_user).order_by("podcast__name")
    return render(request, template_name, context={'user':current_user, 'results':episodes_list, 'followings':followings}) 
   
    
                
def PodcastAnalytics(request,slug):
    template_name = "core/analytics.html"
    current_user = User.objects.get(id=request.user.id)
    podcast = get_object_or_404(Podcast, slug=slug)
    if current_user.id == podcast.owner.id:
        # This is the data i will need to show for each podcast
        average_likes_per_episode = 0
        average_streams_per_episode = 0
        average_comments_per_episode = 0
        follows_in_the_last_week = 0
        total_likes = 0
        total_streams = 0
        total_lengths = 0
        total_comments = 0
        ranking_podcast = 0
        
        episodes_list = []
        today = now()
        last_week_start = today - timedelta(days=today.weekday() + 6)
        last_week_end = today
        week_before_start = last_week_start - timedelta(days=7)
        week_before_end = last_week_end - timedelta(days=7)

        number_of_episodes = podcast.episodes.all().count()
        followers = str(PodcastFollow.objects.filter(user=current_user).all().count())
        follows_in_the_last_week = PodcastFollow.objects.filter(Q(podcast=podcast) & Q(date__gte=last_week_start) & Q(date__lte=last_week_end)).all().count()
        follows_in_the_week_before = PodcastFollow.objects.filter(Q(podcast=podcast) & Q(date__gte=week_before_start) & Q(date__lte=week_before_end)).all().count()
        
        for rank,current_podcast in enumerate(Podcast.objects.annotate(follow_count=Count('podcastfollow')).order_by("-follow_count"), start=1):
            # Find the rank of the podcast based on followers
            if current_podcast.id == podcast.id:
                 ranking_podcast = rank

        if number_of_episodes > 0:
            
            for episode in podcast.episodes.all():
                # For each episode get some data relative to it
                likes_in_the_last_week = EpisodeLike.objects.filter(Q(episode=episode) & Q(date__gte=last_week_start) & Q(date__lte=last_week_end)).all().count()
                streams_in_the_last_week = EpisodeStream.objects.filter(Q(episode=episode) & Q(date__gte=last_week_start) & Q(date__lte=last_week_end)).all().count()
                episode_likes = EpisodeLike.objects.filter(episode=episode).all().count()
                episode_comments = EpisodeComment.objects.filter(episode=episode).all().count() 
                episode_streams = EpisodeStream.objects.filter(episode=episode).all().count() 
                total_lengths += int(episode.length)
                total_streams += episode_streams
                total_likes += episode_likes
                total_comments += episode_comments
                episodes_list.append({'episode':episode, 'likes_in_the_last_week':likes_in_the_last_week, 'streams_in_the_last_week':streams_in_the_last_week, 'total_likes':episode_likes, 'episode_comments':episode_comments, 'episode_streams':episode_streams})

                average_comments_per_episode = int(total_comments / number_of_episodes)
                average_likes_per_episode = int(total_likes / number_of_episodes)
                average_streams_per_episode = int(total_streams / number_of_episodes)
                
        
        return render(request, template_name, context={'user':current_user, 'episodes':episodes_list, 'podcast':podcast, 'average_comments_per_episode':average_comments_per_episode, 'average_likes_per_episode':average_likes_per_episode, 'average_streams_per_episode':average_streams_per_episode, 'total_lengths':total_lengths, 'followers':followers, 'follows_in_the_last_week':follows_in_the_last_week-follows_in_the_week_before, 'ranking_podcast':ranking_podcast})
    else:
        return HttpResponse(status=401)
        
    