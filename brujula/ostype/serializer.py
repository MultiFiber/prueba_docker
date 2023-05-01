from .models import  Ostype
from rest_framework import serializers
from utils.serializers import BaseModelSerializer


class OstypeSerializer(BaseModelSerializer):
    class Meta:
        model = Ostype
        fields = '__all__'