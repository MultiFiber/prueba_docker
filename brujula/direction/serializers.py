from rest_framework import serializers
from utils.serializers import BaseModelSerializer
from .models import Direction


class DirectionSerializers(BaseModelSerializer):

    iso = serializers.SerializerMethodField()

    def get_iso(self, obj):
        if obj.iso:
            return obj.iso.lower()
        return ''

    class Meta:
        model = Direction
        fields = '__all__'


class DirectionSearchSerializers(BaseModelSerializer):

    iso = serializers.SerializerMethodField()

    def get_iso(self, obj):
        if obj.iso:
            return obj.iso.lower()
        return ''

    class Meta:
        model = Direction
        fields = ('name','id','coordinates','iso')


