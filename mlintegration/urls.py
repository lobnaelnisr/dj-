from django.urls import path
from . import views

urlpatterns = [
#path('fetchpredrequirements', views.fetch_prediction_requirements ,name='fetchpredrequirements'),    
path('prediction', views.get_predictions ,name='prediction'),

]