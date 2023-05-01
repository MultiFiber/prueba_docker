from .models import  OperatorSetting
from rest_framework import serializers
from utils.serializers import BaseModelSerializer

__all__ = ['OperatorSettingSerializer', 'OperatorSettingSerializerV2']


class OperatorSettingSerializer(BaseModelSerializer):

    class Meta:
        model = OperatorSetting
        fields = '__all__'


class OperatorSettingSerializerV2(BaseModelSerializer):

    valor = serializers.CharField(source='config')
    
    class Meta:
        model = OperatorSetting
        fields = ['valor']        