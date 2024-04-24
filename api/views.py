#from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import morphSerializers
from .models import morph_data
from rest_framework import status
from django.http import JsonResponse
#from pymongo import MongoClient
#from rest_framework import generics

# API Overview View
@api_view(['GET'])
def showUsersData (request):
    if request.method == 'GET':
        user = morph_data.objects.all()
        serializer = morphSerializers(user, many = True)
        return JsonResponse ({'Users Data ': serializer.data}, safe= False)


@api_view(['POST'])
def saveUserData (request):
    serializer = morphSerializers(data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response (serializer.data, status= status.HTTP_201_CREATED)
##################################################
@api_view(['GET', 'PUT', 'DELETE'])
def edit_info (request, id, format= False):
    try:
        student_data = morph_data.objects.get(pk = id)
    except student_data.DoseNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)  
    
    if request.method =='GET':
        serializer = morphSerializers(student_data)
        return Response(serializer.data)
    

    if request.method =='PUT':
        serializer = morphSerializers(student_data, data = request.data)
        if serializer.is_valid():
            serializer.save
            return Response(serializer.data)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)


    if request.method =='DELETE':
        student_data.delete()
        return Response(status= status.HTTP_204_NO_CONTENT)
#########################################################################################
# API Overview View
@api_view(['GET'])
def api_overview(request):
    """
    Provides an overview of the available API endpoints.
    """
    api_urls = {
        'To show all data': '/view',
        'To add new data ': '/add',
        'To edit data ': '/edit/<id>',
        'the format is ': 'username=  ,arousal=   ,attention=  ,dominantEmotion=  ',
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
      

