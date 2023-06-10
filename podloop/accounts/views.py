
from urllib.parse import urlencode
from django.http import Http404
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
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
        success_message = None
        if request.user.is_authenticated:
            return redirect('core:home')

        # Check if this is a redirect after a password change and notify of the successful password change
        if request.GET.get('success_message'):
            success_message = request.GET.get('success_message')

        form = self.form_class()
        return render(request, self.template_name, context={'form': form, 'success_message': success_message})
        
    def post(self, request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            # Authenticate the user using the provided email and password
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                # If authentication is successful, log the user in and redirect to the home page
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
        # Redirect to the home page if the user is already authenticated
        if request.user.is_authenticated:
            return redirect('core:home')
        
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
        
    def post(self, request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            
            # Get the form data
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            username = form.cleaned_data.get('username')
            name = form.cleaned_data.get('name')
            last_name = form.cleaned_data.get('last_name')
            
            # Check if the username already exists
            if(User.objects.filter(username__iexact=username)):
                message.append('Username already exists')
            
            # Check if the username already exists
            if(User.objects.filter(email__iexact=email)):
                 message.append('Email already exists')     
                 
            # Check if the username already exists
            result_password_validation = Util.validate_password(raw_password)
            
            if result_password_validation != []:
                message.extend(result_password_validation)
                    
            if message != []:
                return render(request, self.template_name, context={'form': form, 'error_message': message})
            
            # Create a new user
            new_user = User(email=email,username=username,name=name,last_name=last_name, is_active=True)
            new_user.set_password(raw_password)
            new_user.save()
            # Generate and save an email verification code
            verify_code = uuid.uuid1()
            new_email_verification = EmailVerification(user=new_user,code=verify_code)
            new_email_verification.save()
            # Send email confirmation to the user
            Util.send_confirm_email(email,verify_code)
            # Send email confirmation to the user
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
        # Check if the verification code exists
        obj = get_object_or_404(EmailVerification, code=code)
        user = User.objects.get(id=obj.user_id)
        # User has verified his email
        user.is_email_verified = True
        user.save()
        # Delete the verification code
        obj.delete()
        return render(request, self.template_name, context={'success_message': 'Email verified successfully'})
       

           
class ChangePasswordView(View):
    template_name = "accounts/change_password.html"
    form_class = ChangePasswordForm
    
    def get(self, request):
        # Render the change password template with an instance of the form
        form = self.form_class()
        return render(request, self.template_name, context={'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        message = []
        if form.is_valid():
            # Get the form data
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
            confirm_new_password = form.cleaned_data.get('confirm_new_password')
            
            # Get the current user object
            current_user = User.objects.get(username=request.user.username)
            
            # Check if the new passwords match
            if new_password != confirm_new_password:
                message.append("The passwords don't match")
            
            # Check if the current password is correct
            if not current_user.check_password(current_password):
                message.append("The current password is not correct")
            
            # Check if the new password is the same as the old password
            if current_user.check_password(new_password):
                message.append("New password cannot be the same as the old one")
                
            # Validate the new password
            password_validation_errors = Util.validate_password(new_password)
            if password_validation_errors:
                message.extend(password_validation_errors)
                
            if message:
                return render(request, self.template_name, context={'form': form, 'error_message': message})   
            else:
                # Set the new password for the current user and save
                current_user.set_password(new_password)
                current_user.save()
                
                # Prepare success message and redirect to login page
                message = "Password changed successfully. Please login to start a new session."
                url = reverse('accounts:login') + '?' + urlencode({'success_message': message})
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
            # Check if the given email exists, if true send the reset email
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
            # Check if the reset password code exists
            obj = get_object_or_404(PasswordReset, code=code)
            user = User.objects.get(id=obj.user_id)
            # Check if the new password is not the same as the old one
            if new_password != confirm_new_password:
                message.append("The passwords don't match")
            # Validate the new password    
            password_validation_errors = Util.validate_password(new_password)
            if password_validation_errors != []:
                message.extend(password_validation_errors)
            # If there are any errors render the form with the errors  
            if message != []:
                return render(request, self.template_name, context={'form': form, 'error_message': message})   
            else:
                # Update the user's password and delete the reset request from database
                user.set_password(new_password)
                user.save()
                obj.delete()
                message = "Password changed successfully, please login to start a new session"
                url = reverse('accounts:login')+ '?' + urlencode({'success_message': message})
                return redirect(url)  
        else:
            message.append("The data is not valid")
            return render(request, self.template_name, context={'form': form, 'error_message': message})        
            
