from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
import datetime
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, username, name, last_name, password, **extra_fields):
        if not email:
            raise ValueError("You have to provide a valid email address")
        
        email = self.normalize_email(email)
        user = self.model(email=email,username=username, last_name=last_name, name=name, **extra_fields)
        user.set_password(password)
    
        user.save(using=self.db)
        print("ho fatto: ", extra_fields.get('is_staff'))
        return user

    def create_user(self, email, username, name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_active',True)
        
        return self._create_user(email, username, name, last_name, password, **extra_fields)
    
    def create_superuser(self, email, username, name, last_name, password, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        
        
        return self._create_user(email, username, name, last_name, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(blank=True, default='', unique=True)
    name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    username = models.CharField(max_length=255, blank=False, unique=True)
    
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now, blank=False)
    last_login =  models.DateTimeField(blank=True, null=True)
    
    link_profile_picture = models.ImageField(upload_to='images/')
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name','last_name','username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def get_full_name(self):
        return self.name + " " + self.last_name
    
    def get_username(self):
        return self.username
    
    
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, blank=False)
    date_created = models.DateTimeField(default=now, blank=False)

    class Meta:
        verbose_name_plural = "Email verifications" 
        
    
class PasswordReset(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, blank=False)
    date_created = models.DateTimeField(default=now, blank=False)

    class Meta:
        verbose_name_plural = "Password resets" 
    
