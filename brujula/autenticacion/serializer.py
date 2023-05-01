from django.contrib.auth.models import User
from rest_framework import serializers
from utils.serializers import BaseModelSerializer


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = '__all__'