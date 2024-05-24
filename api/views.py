from rest_framework.response import Response 
from .models import SessionData
from .serializers import SessionDataSerializer
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from django.db.models import Max
from datetime import datetime 
import re



# API Overview View
@api_view(['POST'])
def create( request):
    if request.method == 'POST':
        serializer = SessionDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


@api_view(['GET'])    
def list( request):
    if request.method == 'GET':
        queryset = SessionData.objects.all()
        serializer = SessionDataSerializer(queryset, many=True)
        return JsonResponse({'users-data':serializer.data}, safe= False)


@api_view(['GET'])
def api_overview(request):
    """
    overview of the available API endpoints.
    """
    api_urls = {
        'To show all data': '/view',
        'To add new data ': '/add',
        'to show all users': 'users/',
        'to login to your account ': 'login/',
        'to sign-up for the first time ': 'signup/',
        'to test token validity ': 'test_token/',
        'to reset your password':'reset_password/',
        'to change your password': 'change_password/',
        'to change user status':'suspend_users/',
        'to add users manually':'add_user/',
        'to change user status':'suspend_users/',
        'to view each session details':'unique/',
        'to view total time spent by each user ':'total_sessions_duration/',

        
    }
    return Response(api_urls)

## Separate records of each session to each user:

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

# each session duration: 

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
            'Session_Duration':session_duration_minutes,
            'Session_Duration_Txt': session_duration_str
        })

    return Response(unique_sessions)


#adjust time format:

def parse_time(time_str):
    match = re.match(r'(\d+):(\d+):(\d+)(?:\.(\d+))?', time_str)
    if match:
        if match.group(4):
            return datetime.strptime(time_str, '%H:%M:%S.%f')
        else:
            return datetime.strptime(time_str, '%H:%M:%S')
    else:
        raise ValueError("Invalid time format: {}".format(time_str))
    

#User cumulative sessions time

@api_view(['GET'])
def total_sessions_duration(request):
    session_durations = []
    email_total_durations = {}

    data = SessionData.objects.values('userEmail', 'SessionStartedAt').annotate(Max('CaptureTime'))

    for entry in data:
        email = entry['userEmail']
        session_start = parse_time(entry['SessionStartedAt'])
        capture_time = entry['CaptureTime__max']
        if capture_time:
            capture_time = parse_time(capture_time)
            session_duration_seconds = (capture_time - session_start).total_seconds()
            session_duration_minutes = session_duration_seconds / 60
            session_duration_str = f"{session_duration_minutes:.2f} minutes"  # Format session duration
        else:
            session_duration_str = "0 minutes"

        session_durations.append({
            'userEmail': email,
            'Session_Duration': session_duration_minutes,
            'Session_Duration_Txt': session_duration_str
        })

        if email in email_total_durations:
            email_total_durations[email] += session_duration_minutes
        else:
            email_total_durations[email] = session_duration_minutes

    total_durations = [
        {'userEmail': email, 'Total_Session_Duration': total_duration, 'Total_Session_Duration_Txt': f"{total_duration:.2f} minutes"}
        for email, total_duration in email_total_durations.items()
    ]

    return Response(total_durations)

