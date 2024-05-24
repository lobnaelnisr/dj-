from django.urls import path
from . import views

urlpatterns = [
    path('fetchquiz', views.fetch_user_data ,name='fetchquiz'),
    path('fetchassignment', views.fetch_user_assignmentdata ,name='fetchassignment'),
    path('fetchsession', views.fetch_user_sessiondata ,name='fetchsession'),
]