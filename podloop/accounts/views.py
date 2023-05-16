
from urllib.parse import urlencode
from django.http import Http404
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from .forms import LoginForm,RegisterForm,ChangePasswordForm,PasswordModifyForm,RequestResetPasswordForm
from django.contrib.auth import authenticate,login,get_user_model
from accounts.models import EmailVerification,PasswordReset
from accounts.utils import Util
import uuid
# Create your views here.

User = get_user_model()

class LoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')

        #Nel caso questo fosse un redirect dopo cambi password,avvertire del successo del cambio password
        success_password_change = request.GET.get('success_message')
        form = self.form_class()
        return render(request, self.template_name, context={'form': form, 'password_change':success_password_change})
        
    def post(self, request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('core:home')
            else:
                message = 'User not found'
        else:
            message = "The data is not valid"
            
        return render(request, self.template_name, context={'form': form, 'error_message': message})
    

class RegisterView(View):
    template_name = 'accounts/register.html'
    form_class = RegisterForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
        
    def post(self, request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            
            #prendo i dati del form
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            username = form.cleaned_data.get('username')
            name = form.cleaned_data.get('name')
            last_name = form.cleaned_data.get('last_name')
            
            #controllo username se esiste già
            if(User.objects.filter(username__iexact=username)):
                message.append('Username already exists')
            
            #controllo email se esiste già
            if(User.objects.filter(email__iexact=email)):
                 message.append('Email already exists')     
                 
            #controllo password se è valida
            result_password_validation = Util.validate_password(raw_password)
            
            if result_password_validation != []:
                message.extend(result_password_validation)
                    
            if message != []:
                return render(request, self.template_name, context={'form': form, 'error_message': message})
            
            
            new_user = User(email=email,username=username,name=name,last_name=last_name, is_active=True)
            new_user.set_password(raw_password)
            new_user.save()
            
            verify_code = uuid.uuid1()
            new_email_verification = EmailVerification(user=new_user,code=verify_code)
            new_email_verification.save()
            
            Util.send_confirm_email(email,verify_code)
            
            user = authenticate(email=email, password=raw_password)
            if user is not None:
                login(request, user)
                return redirect('core:home')
            else:
                message.append('Something went wrong, please retry')
                return render(request, self.template_name, context={'form': form, 'error_message': message})
        else:
            message.append("The data is not valid")
            return render(request, self.template_name, context={'form': form, 'error_message': message})


    


class ConfirmEmailView(View):
    template_name = "accounts/confirm_email.html"
    def get(self,request,code):
        try:
            obj = get_object_or_404(EmailVerification, code=code)
            user = User.objects.get(id=obj.user_id)
            user.is_email_verified = True
            user.save()
            obj.delete()
            return render(request, self.template_name, context={'success_message': 'Email verified successfully'})
        except EmailVerification.DoesNotExist:
            raise Http404("Invalid verification code")

           
class ChangePasswordView(View):
    template_name = "accounts/change_password.html"
    form_class = ChangePasswordForm
    
    def get(self, request):
        
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
    
    def post(self,request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            confirm_new_password = form.cleaned_data.get('confirm_new_password')
            current_user = User.objects.get(username=request.user.username)
            
            if new_password != confirm_new_password:
                message.append("The passwords don't match")
            
            if not current_user.check_password(current_password):
                message.append("The current password is not correct")
            
            if current_user.check_password(new_password):
                message.append("New password cannot be the same as the old one")
                
            password_validation_errors = Util.validate_password(new_password)
            if password_validation_errors != []:
                message.extend(password_validation_errors)
                
            if message != []:
                return render(request, self.template_name, context={'form': form, 'error_message': message})   
            else:
                current_user.set_password(new_password)
                current_user.save()
                message = "Password changed successfully, please login to start a new session"
                url = reverse('accounts:login')+ '?' + urlencode({'success_message': message})
                return redirect(url)  
        else:
            message.append("The data is not valid")
            return render(request, self.template_name, context={'form': form, 'error_message': message})


class RequestResetPasswordView(View):
    template_name = "accounts/request_reset_password.html"
    form_class = RequestResetPasswordForm
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
                reset_code = uuid.uuid1()
                new_password_reset = PasswordReset(user=user,code=reset_code)
                new_password_reset.save()
                
                Util.send_reset_email(email,reset_code)
            except User.DoesNotExist:
                pass
            finally:
                message = "If there's an account with this email, you will receive a link to reset the password"
                return render(request, self.template_name, context={'form': form, 'message': message}) 
        else:
            message = "The data is not valid"
            return render(request, self.template_name, context={'form': form, 'error_message': message})
            
class ResetPassword(View):
    template_name = "accounts/change_password.html"
    form_class = PasswordModifyForm
    
    def get(self, request, email, code):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
    
    def post(self,request, email, code):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            confirm_new_password = form.cleaned_data.get('confirm_new_password')
            obj = get_object_or_404(PasswordReset, code=code)
            user = User.objects.get(id=obj.user_id)
            if new_password != confirm_new_password:
                message.append("The passwords don't match")
                 
            password_validation_errors = Util.validate_password(new_password)
            if password_validation_errors != []:
                message.extend(password_validation_errors)
                
            if message != []:
                return render(request, self.template_name, context={'form': form, 'error_message': message})   
            else:
                user.set_password(new_password)
                user.save()
                message = "Password changed successfully, please login to start a new session"
                url = reverse('accounts:login')+ '?' + urlencode({'success_message': message})
                return redirect(url)  
        else:
            message.append("The data is not valid")
            return render(request, self.template_name, context={'form': form, 'error_message': message})        
            
