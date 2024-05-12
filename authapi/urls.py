from django.urls import re_path
from . import views
from .views import UserListView
from django.contrib.auth import views as auth_views    #



urlpatterns = [
    re_path('login/', views.login),
    re_path('signup/', views.signup),
    re_path('test_token/', views.test_token),
    re_path('users/', UserListView.as_view(), name='user-list'),
    #forget password 
    #re_path('reset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
    #re_path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    #re_path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    #re_path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),


]
