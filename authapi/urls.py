from django.urls import re_path
from . import views
from .views import UserListView

urlpatterns = [
    re_path('login/', views.login),
    re_path('signup/', views.signup),
    re_path('test_token/', views.test_token),
    re_path('users/', UserListView.as_view(), name='user-list'),

]
