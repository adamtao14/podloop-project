from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import LoginView, RegisterView,ConfirmEmailView,ChangePasswordView,RequestResetPasswordView,ResetPassword
from django.contrib.auth.views import LogoutView 
from django.contrib.auth.decorators import login_required
app_name = "accounts"
urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('confirm-email/<str:code>', ConfirmEmailView.as_view(), name="confirm-email"),
    path('change-password/', login_required(ChangePasswordView.as_view()), name="change-password"),
    path('reset-password/', RequestResetPasswordView.as_view(), name="reset-password"),
    path('reset-password/<str:email>/<str:code>', ResetPassword.as_view(), name="reset-password-confirm"),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)