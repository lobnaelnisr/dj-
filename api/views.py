from rest_framework import viewsets # type: ignore
from rest_framework.response import Response # type: ignore
from .models import SessionData
from .serializers import SessionDataSerializer
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.db.models import Max
from datetime import datetime
import re
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

## Separate records with the same email & start time

@api_view(['GET'])
def separate_records(request):
    user_data = SessionData.objects.all()
    separated_data = {}
    for data in user_data:
        key = (data.userEmail, data.SessionStartedAt)
        if key not in separated_data:
            separated_data[key] = {'records': [], 'last_record': None}
        separated_data[key]['records'].append(data)
        separated_data[key]['last_record'] = data

    serialized_data = []
    for email, session_data in separated_data.items():
        serialized_session = {
            'email': email,
            'records': SessionDataSerializer(session_data['records'], many=True).data,
            'last_record': SessionDataSerializer(session_data['last_record']).data
        }
        serialized_data.append(serialized_session)

    return Response(serialized_data)

#last record only 

#SessionData
@api_view(['GET'])
def unique(request):
    unique_sessions = []
    data = SessionData.objects.values('userEmail', 'SessionStartedAt').annotate(Max('CaptureTime'))

    for entry in data:
        email = entry['userEmail']
        session_start = parse_time(entry['SessionStartedAt'])
        start = entry['SessionStartedAt']
        end = entry['CaptureTime__max']
        capture_time = entry['CaptureTime__max']
        if capture_time:
            capture_time = parse_time(capture_time)
            session_duration_seconds = (capture_time - session_start).total_seconds()
            session_duration_minutes = session_duration_seconds / 60
            session_duration_str = f"{session_duration_minutes:.2f} minutes"  # Format session duration
        else:
            session_duration_str = "0 minutes"

        unique_sessions.append({
            'userEmail': email,
            'Session_Started': start,
            'Session_Ended': end,
            'Session_Duration': session_duration_str
        })

    return Response(unique_sessions)

def parse_time(time_str):
    match = re.match(r'(\d+):(\d+):(\d+)(?:\.(\d+))?', time_str)
    if match:
        if match.group(4):
            return datetime.strptime(time_str, '%H:%M:%S.%f')
        else:
            return datetime.strptime(time_str, '%H:%M:%S')
    else:
        raise ValueError("Invalid time format: {}".format(time_str))