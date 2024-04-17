from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import generics
from .models import MyModel
from .serializers import MyModelSerializer
from pymongo import MongoClient



# Create your views here.
def index(request):
    return render(request , 'pages/index.html' , {'name':'ahmed'})

def about(request):
    pass

def home(request):
    return HttpResponse("Welcome to the homepage!")

class MyModelListCreate(generics.ListCreateAPIView):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

    def perform_create(self, serializer):
        serializer.save()
    def get_queryset(self):
        client = MongoClient('mongodb+srv://lobnaelnisr:1234lolo@cluster0.9evcfxw.mongodb.net/')
        db = client['mgdb']
        collection = db['students']
        return list(collection.find())  
      

