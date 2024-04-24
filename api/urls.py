#from django.contrib import admin   
from django.urls import path, re_path
from .views import api_overview            #, students_list, student_detail
from . import views
#from .views import MyModelListCreate

urlpatterns = [

    # API Overview
    path('', api_overview, name='api_overview'),

    re_path('add/', views.saveUserData),
    re_path('view/', views.showUsersData),
    re_path('edit/<int:id>', views.edit_info),
    #path('api/data/', MyModelListCreate.as_view(), name='my_model-list-create'),
    
]
#hello
#urlpatterns = format_suffix_patterns(urlpatterns)
