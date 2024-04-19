# serializers.py

from rest_framework import serializers
from .models import student_data

class studentSerializers(serializers.ModelSerializer):
    class Meta:
        model = student_data
        #fields = '__all__'
        fields = ['id', 'username', 'email'] 
        