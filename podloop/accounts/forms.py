from django import forms

class LoginForm(forms.Form):
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    

class RegisterForm(forms.Form):
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class':'form-control mb-3'}))
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class':'form-control mb-3'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))

class RequestResetPasswordForm(forms.Form):
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class':'form-control mb-3'}))

class PasswordModifyForm(forms.Form):
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    confirm_new_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    class Meta:
        abstract = True
        
class ChangePasswordForm(PasswordModifyForm):
    current_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class':'form-control mb-3'}))
    
