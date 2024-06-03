from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('', include('authapi.urls')),
    path('', include('fetchapi.urls')),
    path('', include('mlintegration.urls')),

    
]

urlpatterns += staticfiles_urlpatterns()   #


