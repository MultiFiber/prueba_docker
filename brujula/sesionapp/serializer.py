from .models import  HistorySession
from rest_framework import serializers
from utils.serializers import BaseModelSerializer


class HistorySessionSerializer(BaseModelSerializer):
    class Meta:
        model = HistorySession
        fields = '__all__'