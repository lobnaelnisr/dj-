from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger('__name__')

#@csrf_exempt
def fetch_user_data(request):
    #try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT stu.id AS student_id, stu.username, q.id AS quiz_id, q.name AS quiz_name, qa.sumgrades
                FROM whole_proj.Students stu
                JOIN whole_proj.Quiz_Attempts qa ON stu.id = qa.userid
                JOIN whole_proj.Quiz q ON qa.quiz = q.id
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
        return JsonResponse({'data': data}, safe=False)
    
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
        return JsonResponse({'data2': data2}, safe=False)
    except Exception as e:
        logger.error(f"Error fetching user session data: {e}")
        return JsonResponse({'error': 'Error fetching user session data'}, status=500)
    
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
        return JsonResponse({'data3': data3}, safe=False)
    except Exception as e:
        logger.error(f"Error fetching user session data: {e}")
        return JsonResponse({'error': 'Error fetching user session data'}, status=500)    
