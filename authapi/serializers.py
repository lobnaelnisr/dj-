from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializers(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id','username', 'email','password']
        

class UserListSerializers(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'email']          