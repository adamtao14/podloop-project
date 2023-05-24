from django import forms

class ProfileForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class':'form-control mb-3'}))
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    link_profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'form-control mb-3'}))
    
class PodcastForm(forms.Form):
    name = forms.CharField(required=True,max_length=300, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    description = forms.CharField(required=True, max_length=500, widget=forms.Textarea(attrs={'class':'form-control mb-3'}))
    podcast_thumbnail = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'form-control mb-3'}))
    categories = forms.MultipleChoiceField(required=True)
    
    def __init__(self, choices, *args, **kwargs):
        super(PodcastForm, self).__init__(*args, **kwargs)
        self.fields['categories'].choices = choices
        
class EpisodeForm(forms.Form):
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    description = forms.CharField(required=True, max_length=200, widget=forms.Textarea(attrs={'class':'form-control mb-3'}))
    episode_thumbnail = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'form-control mb-3'}))
    is_private = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check mb-3 me-auto'}))
    audio = forms.FileField(required=True,widget=forms.FileInput(attrs={'class':'form-control mb-3'}))
    length = forms.CharField(required=False, label="",widget=forms.HiddenInput(attrs={'class':'form-control mb-3'}))
    
class EpisodeEditForm(forms.Form):
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    description = forms.CharField(required=True, max_length=200, widget=forms.Textarea(attrs={'class':'form-control mb-3'}))
    episode_thumbnail = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class':'form-control mb-3'}))
    is_private = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check mb-3 me-auto'}))
    
class PlaylistForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    description = forms.CharField(required=False, max_length=200, widget=forms.Textarea(attrs={'class':'form-control mb-3'}))
    is_private = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check mb-3 me-auto'}))