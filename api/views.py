from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import studentSerializers
from .models import student_data
#from django.http import HttpResponse
#from django.http import JsonResponse
#from pymongo import MongoClient
#from rest_framework import generics

# API Overview View
@api_view(['GET'])
def api_overview(request):
    #Provides an overview of the available API endpoints.
    api_urls = {
        'Get All Students and create': '/students/',
        'detail delete update student': '/students/<id>/',
    }
    return Response(api_urls)

# CRUD Views for Students
@api_view(['GET', 'POST'])
def students_list(request):
    #List all students or create a new student.
    if request.method == 'GET':
        students = student_data.objects.all()
        serializer = studentSerializers(students, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = studentSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def student_detail(request, id):
    #Retrieve, update or delete a student instance.
    try:
        student = student_data.objects.get(pk=id)
    except student_data.DoesNotExist:
        return Response({'error': 'Student not found'}, status=404)

    if request.method == 'GET':
        serializer = studentSerializers(student)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = studentSerializers(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        student.delete()
        return Response({'message': 'Student deleted successfully'}, status=204)


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
      

