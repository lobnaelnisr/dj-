from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls')),
    path('', include('authapi.urls')),
    path('', include('fetchapi.urls')),
    #path('api-auth/', include('rest_framework.urls'))
]

urlpatterns += staticfiles_urlpatterns()   #


