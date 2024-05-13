from rest_framework import viewsets # type: ignore
from rest_framework.response import Response # type: ignore
from .models import SessionData
from .serializers import SessionDataSerializer
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
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
        return JsonResponse({'users-data':serializer.data}, safe= False)

@api_view(['GET'])
def api_overview(request):
    """
    Provides an overview of the available API endpoints.
    """
    api_urls = {
        'To show all data': '/view',
        'To add new data ': '/add',
        'morph data format ': '{ "CaptureTime":"0","SessionEndedAt":" 0" ,"SessionStartedAt":" 0" ,"arousal":" 0"   ,"attention":" 0"  ,"dominantEmotion": " txt" , "volume":" 0" , "SessionEndedAt":" 0"}',
        'to login to your account ': 'login/',
        'login format':'{ "username": "test", "password": "0000" }',
        'to sign-up for the first time ': 'signup/',
        'signup format':'{ "username": "test", "password": "0000" , "email": "test@email.co" }',
        'to test token validity ': 'test_token/',
        'to show all users': 'users/',
        'to reset your password':'reset_password/',
        
    }
    return Response(api_urls)

