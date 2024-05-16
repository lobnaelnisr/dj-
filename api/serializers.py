# serializers.py

from rest_framework import serializers # type: ignore
from .models import SessionData

class SessionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionData
        fields = '__all__'
        
        