from django.urls import path
from . import views

from .views import MyModelListCreate


urlpatterns = [
    path('' , views.index , name= 'index') ,
    path('about' , views.about , name= 'about') ,
    
]

urlpatterns = [
    path('api/data/', MyModelListCreate.as_view(), name='my_model-list-create'),

]
