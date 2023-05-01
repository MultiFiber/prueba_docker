from rest_framework import serializers
from .models import Operator
from utils.serializers import BaseModelSerializer


class OperatorSerializers(BaseModelSerializer):
    class Meta:
        model = Operator
        fields = '__all__'

     