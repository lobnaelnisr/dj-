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


#adjust time format:
arabic_to_english = {
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'
}

def convert_arabic_to_english(time_str):
    return ''.join(arabic_to_english.get(char, char) for char in time_str)

def parse_time(time_str):
    if not time_str:
        raise ValueError("Time string is empty")
    
    time_str = convert_arabic_to_english(time_str)
    match = re.match(r'(\d+):(\d+):(\d+)(?:\.(\d+))?', time_str)
    if match:
        if match.group(4):
            return datetime.strptime(time_str, '%H:%M:%S.%f')
        else:
            return datetime.strptime(time_str, '%H:%M:%S')
    else:
        raise ValueError("Invalid time format: {}".format(time_str))
    

@api_view(['POST'])
def create(request):
    if request.method == 'POST':
        # Convert Arabic numerals to English numerals for relevant fields
        data = request.data.copy()
        if 'CaptureTime' in data:
            data['CaptureTime'] = convert_arabic_to_english(data['CaptureTime'])
        if 'SessionEndedAt' in data:
            data['SessionEndedAt'] = convert_arabic_to_english(data['SessionEndedAt'])
        if 'SessionStartedAt' in data:
            data['SessionStartedAt'] = convert_arabic_to_english(data['SessionStartedAt'])

        serializer = SessionDataSerializer(data=data)
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
        session_start = entry['SessionStartedAt']
        capture_time = entry['CaptureTime__max']

        try:
            session_start_parsed = parse_time(session_start)
            if capture_time:
                capture_time_parsed = parse_time(capture_time)
                session_duration_seconds = (capture_time_parsed - session_start_parsed).total_seconds()
                session_duration_minutes = session_duration_seconds / 60
                session_duration_str = f"{session_duration_minutes:.2f} minutes"
            else:
                session_duration_minutes = 0
                session_duration_str = "0 minutes"

            unique_sessions.append({
                'userEmail': email,
                'Session_Started': session_start,
                'Session_Ended': capture_time,
                'Session_Duration': session_duration_minutes,
                'Session_Duration_Txt': session_duration_str
            })

        except ValueError as e:
            print(f"Error parsing time for email {email}: {e}")

    return Response(unique_sessions)


#User cumulative sessions time

@api_view(['GET'])
def total_sessions_duration(request):
    session_durations = []
    email_total_durations = {}

    data = SessionData.objects.values('userEmail', 'SessionStartedAt').annotate(Max('CaptureTime'))

    for entry in data:
        email = entry['userEmail']
        session_start = entry['SessionStartedAt']
        capture_time = entry['CaptureTime__max']

        try:
            session_start_parsed = parse_time(session_start)
            if capture_time:
                capture_time_parsed = parse_time(capture_time)
                session_duration_seconds = (capture_time_parsed - session_start_parsed).total_seconds()
                session_duration_minutes = session_duration_seconds / 60
                session_duration_str = f"{session_duration_minutes:.2f} minutes"
            else:
                session_duration_minutes = 0
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

        except ValueError as e:
            print(f"Error parsing time for email {email}: {e}")

    total_durations = [
        {'userEmail': email, 'Total_Session_Duration': total_duration, 'Total_Session_Duration_Txt': f"{total_duration:.2f} minutes"}
        for email, total_duration in email_total_durations.items()
    ]

    return Response(total_durations)