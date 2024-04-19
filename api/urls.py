#from django.contrib import admin   
from django.urls import path
from .views import api_overview, students_list, student_detail
#from . import views
#from .views import MyModelListCreate

urlpatterns = [

    # API Overview
    path('', api_overview, name='api_overview'),

    # Students List and Create
    path('students/', students_list, name='students_list'),
    # Student Detail, Update, and Delete
    path('students/<int:id>/', student_detail, name='student_detail')

    #path('api/data/', MyModelListCreate.as_view(), name='my_model-list-create'),

]
#hello
#urlpatterns = format_suffix_patterns(urlpatterns)
