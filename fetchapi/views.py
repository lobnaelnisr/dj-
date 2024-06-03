from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger('__name__')

#@csrf_exempt
def fetch_user_quizdata(request):
    #try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT stu.username, stu.email, q.Quiz_Name, c.Course, cs.Semester, qa.sumgrades
                FROM whole_proj.Students stu
                JOIN whole_proj.Quiz_Attempts qa ON stu.id = qa.userid
                JOIN whole_proj.Quiz q ON qa.quiz = q.id
                JOIN whole_proj.Course c ON q.course = c.id
                JOIN whole_proj.Course_Semester cs ON c.category = cs.id
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
        return JsonResponse( data, safe=False)
    
@csrf_exempt
def fetch_user_assignmentdata(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT stu.id, stu.username, stu.email, a.name, sub.status, sub.timecreated
                FROM whole_proj.Students stu
                JOIN whole_proj.Assign_Submission sub ON stu.id = sub.userid
                JOIN whole_proj.Assign a ON sub.assignment = a.id
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data2 = [dict(zip(columns, row)) for row in rows]
        return JsonResponse(data2, safe=False)
    except Exception as e:
        logger.error(f"Error fetching user assignment data: {e}")
        return JsonResponse({'error': 'Error fetching user assignment data'}, status=500)
    
@csrf_exempt
def fetch_user_sessiondata(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT stu.id, stu.username, stu.email, se.arousal, se.attention, se.dominantEmotion, se.Session_For
                FROM whole_proj.Students stu
                JOIN whole_proj.Session se ON stu.email = se.userEmail
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data3 = [dict(zip(columns, row)) for row in rows]
        return JsonResponse( data3, safe=False)
    except Exception as e:
        logger.error(f"Error fetching user session data: {e}")
        return JsonResponse({'error': 'Error fetching user session data'}, status=500)    
    
@csrf_exempt
def fetch_user_data(request):
    try:
        with connection.cursor() as cursor:
            # Fetch field names from stu_info_field
            cursor.execute("SELECT id, name FROM whole_proj.stu_info_field")
            field_names = cursor.fetchall()
            field_map = {field_id: field_name for field_id, field_name in field_names}

            # Fetch data from Students and stu_info_data
            cursor.execute("""
                SELECT stu.id, stu.username, stu.email, sid.fieldid, sid.data
                FROM whole_proj.Students stu
                LEFT JOIN whole_proj.stu_info_data sid ON stu.id = sid.userid
            """)
            rows = cursor.fetchall()

            # Transform rows into a dictionary with dynamic fields
            user_data = {}
            for row in rows:
                user_id, username, email, fieldid, data = row
                if user_id not in user_data:
                    user_data[user_id] = {
                        'id': user_id,
                        'username': username,
                        'email': email
                    }
                if fieldid and fieldid in field_map:
                    field_name = field_map[fieldid]
                    user_data[user_id][field_name] = data

            # Convert the dictionary to a list for JSON response
            data4 = list(user_data.values())

        return JsonResponse(data4, safe=False)
    except Exception as e:
        logger.error(f"Error fetching user data: {e}")
        return JsonResponse({'error': 'Error fetching user data'}, status=500)

#@csrf_exempt
def fetch_user_coursedata(request):
    #try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id, cs.Semester, c.Course_Name
                FROM whole_proj.Course c
                JOIN whole_proj.Course_Semester cs ON c.category = cs.id
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data5 = [dict(zip(columns, row)) for row in rows]
        return JsonResponse( data5, safe=False)
    