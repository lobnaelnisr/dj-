from django.urls import re_path, path
from . import views
from .views import UserListView, MyPasswordResetCompleteView,external_link_view
from django.contrib.auth import views as auth_views    #




urlpatterns = [
    re_path('login/', views.login),
    re_path('signup/', views.signup),
    re_path('test_token/', views.test_token),
    re_path('users/', UserListView.as_view(), name='user-list'),

    path('external-link/', external_link_view, name='external-link-url'),
    # forget password :
    path('reset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('accounts/reset/done/', MyPasswordResetCompleteView.as_view(), name="password_reset_complete"),


]
