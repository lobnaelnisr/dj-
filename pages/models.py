#from django.db import models
from django.db import models


# Create your models here.
class MyModel(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()

    class Meta:
        db_table = 'my_collection'



# serializers.py

#from rest_framework import serializers
#from .models import MyModel

#class MyModelSerializer(serializers.ModelSerializer):
 #   class Meta:
  #      model = MyModel
   #     fields = '__all__' 

