from django.urls import path
from . import views

urlpatterns = [
#path('fetchpredrequirements', views.fetch_prediction_requirements ,name='fetchpredrequirements'),    
path('successprediction', views.get_predictions ,name='successprediction'),
path('gradeprediction', views.get_predictionsforgrades ,name='gradeprediction'),

]