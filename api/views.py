#from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework import viewsets # type: ignore
from .models import SessionData
from .serializers import SessionDataSerializer
from django.http import JsonResponse
#from pymongo import MongoClient
#from rest_framework import generics

# API Overview View
@api_view(['POST'])
def create( request):
    if request.method == 'POST':
        serializer = SessionDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) # type: ignore
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # type: ignore


@api_view(['GET'])    
def list( request):
    if request.method == 'GET':
        queryset = SessionData.objects.all()
        serializer = SessionDataSerializer(queryset, many=True)
        return JsonResponse({'Users Data ': serializer.data}, safe= False)

@api_view(['GET'])
def api_overview(request):
    """
    Provides an overview of the available API endpoints.
    """
    api_urls = {
        'To show all data': '/view',
        'To add new data ': '/add',
        'the format is ': 'SessionStartedAt=  ,arousal=   ,attention=  ,dominantEmotion= , volume=  ,dominantEmotion=  , feature_1=  , feature_2=  ,feature_3=  ,feature_4=  ,feature_5=  , userName=  , valence=  , volume=  ',
    }
    return Response(api_urls)
#class MyModelListCreate(generics.ListCreateAPIView):
    #queryset = MyModel.objects.all()
    #serializer_class = MyModelSerializer

    #def perform_create(self, serializer):
        #serializer.save()
    #def get_queryset(self):
        #client = MongoClient('mongodb+srv://lobnaelnisr:1234lolo@cluster0.9evcfxw.mongodb.net/')
        #db = client['mgdb']
        #collection = db['students']
        #return list(collection.find())  
      

