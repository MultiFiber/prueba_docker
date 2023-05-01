from rest_framework import serializers
from .models import Category, ResponseOs
from django.http import JsonResponse
from utils.serializers import BaseModelSerializer

__all__ = ['CategorySerializers', 'ResponseOsSerializersV1', 'ResponseOsSerializersV2']



class CategorySerializers(BaseModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ResponseOsSerializersV1(BaseModelSerializer):
    class Meta:
        model = ResponseOs
        fields = '__all__'


class ResponseOsSerializersV2(BaseModelSerializer):

    def create(self, validated_data):

        if 'value' not in validated_data['questions']:
            raise serializers.ValidationError({'message':'Campo questions debe tener clave value'})

        original_res = validated_data['questions']['value']
        respuestas = []
        for index, value in enumerate(original_res):

            if type(value) == bool:
                respuestas.append({
                    'type':1,
                    'value':value
                })
            else:
                respuestas.append({
                    'type':2,
                    'value':value
                })
                
        validated_data['questions']['value'] = respuestas
        return super().create(validated_data)

    class Meta:
        model = ResponseOs
        fields = '__all__'