# serializers.py

from rest_framework import serializers
from .models import morph_data

class morphSerializers(serializers.ModelSerializer):
    class Meta:
        model = morph_data
        #fields = '__all__'
        fields = ['id','username', 'arousal', 'attention','valence', 'volume', 'dominantEmotion' ,'time', 'date']