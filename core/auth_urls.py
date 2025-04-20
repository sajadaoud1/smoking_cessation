from django.urls import path
from core.views import RegisterUserView, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:reset_token>/', ResetPasswordView.as_view(), name='reset-password'),
]
