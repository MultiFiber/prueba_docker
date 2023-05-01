import requests
from rest_framework import serializers
from OS.models import Client, Os, OsPic, Displacement, OperatorPlans, TripSummary, status as status_os
from operator_setting.models import OperatorSetting
from ostype.models import Ostype
from tecnico.models import Technician
from category.models import Category
from operador.models import Operator
from django.db import models
from rest_framework.test import APIClient
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from utils.serializers import BaseModelSerializer, Base64ImageField


__all__ = ['OsSerializers', 'OsPicSerializers', 'DisplacementSerializers',
           'CreateOsSerializers','DetailOsSerializers', 'ClientSerializers']


class ClientSerializers(BaseModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class OsSerializers(BaseModelSerializer):
    class Meta:
        model = Os
        fields = '__all__'


class DetailOsSerializers(BaseModelSerializer):
    name = serializers.CharField(read_only=True)
    direction = serializers.CharField(read_only=True)
    phone = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only= True)
    document_number = serializers.IntegerField(read_only=True)
    service_number = serializers.IntegerField(read_only=True)
    operator_name = serializers.CharField(source="operator.name") 
    category_name = serializers.CharField(source="category.name") 
    technician_name = serializers.CharField(source="technician.full_name") 
    status_name = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()


    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_coordinates(self, obj):
        return obj.get_status_display()

    def get_plan_name(self, obj):
        return 0

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.user_brujula == '' or instance.user_brujula is None:
            data = self.to_representation_userexternal(data, instance)
        else:
            data = self.to_representation_userbrujula(data, instance)

        not_has_id = instance.plan_id=='' or instance.plan_id==' ' or instance.plan_id=='0' or instance.plan_id==None
        if not_has_id:
            try:
                data['plan_name'] = instance.plan_brujula.tradename
            except Exception as e:
                data['plan_name'] = ''
            
        else:
            settings = OperatorSetting.objects.get(operator=instance.technician.operator)
            if 'operator_oraculo_plans_url' not in settings.config:
                data['plan_name'] = '-'
                return data

            url = settings.config['operator_oraculo_plans_url'].replace('&operator',f',ID={instance.plan_id}&operator')\
            .format(instance.technician.operator)
            peticion = requests.get(url,headers={"Authorization":f"{settings.config['operator_oraculo_plans_token']}"})
            if peticion.status_code == 200:
                data['plan_name'] = peticion.json[0].tradename
            else:
                data['plan_name'] = '--'

        return data

    def to_representation_userbrujula(self, data, instance):
        data['name'] = instance.user_brujula.first_name
        data['direction'] = instance.user_brujula.direction_text
        data['phone'] = instance.user_brujula.phone
        data['email'] = instance.user_brujula.email
        data['document_number'] = instance.user_brujula.document_number
        data['service_number'] = instance.user_brujula.service_number
        data['ostype'] = instance.ostype.name
        data
        # Sino viene el usuario de brujula la data de coordinates 
        # Debe venir en la petición externa
        if instance.direction is not None and instance.direction.coordinates is not None:
            data['coordinates'] = instance.direction.coordinates
        elif hasattr(instance.user_brujula, 'ID'):
            data['coordinates'] = instance.user_brujula.direction.coordinates
        else:
            data['coordinates'] = {}
        return data

    def to_representation_userexternal(self, data, instance):
        try:
            settings = OperatorSetting.objects.get(operator=instance.technician.operator)

            peticion = requests.get(settings.config['operator_user_id_url'] + str(instance.user_id),
                                    json=data ,
                                    headers={"Authorization":f"{settings.config['operator_authorization_token']}"})
            #print (settings.config['operator_user_id_url']+ str(instance.user_id))
            #print (instance.technician.operator)

            if peticion.status_code == 200:
                info = peticion.json()    
                data['name'] = info.get('name',' ')
                data['direction'] = info.get('direction',' ')
                data['coordinates'] = info.get('coordinates',{})
                data['phone'] = info.get('phone',' ')
                data['email'] = info.get('email',' ')
                data['document_number'] = info.get('document_number',' ')
                data['service_number'] = info.get('service_number',' ')
                data['ostype'] = instance.ostype.name
            else:
                #print ("peticion a oraculo {}".format(peticion.status_code))
                #print (peticion.json())
                data['name'] = '-'
                data['direction'] = '-'
                data['coordinates'] = {}
                data['phone'] = '-'
                data['email'] = '-'
                data['document_number'] = '-'
                data['service_number'] = '-'

        except OperatorSetting.DoesNotExist:
            #print ('operator no existe {}'.format(instance.technician.operator) )
            data['name'] = '-'
            data['direction'] = '-'
            data['coordinates'] = {}
            data['phone'] = '-'
            data['email'] = '-'
            data['document_number'] = '-'
            data['service_number'] = '-'
        return data 


    class Meta:
        model = Os
        fields = ('status', 'technician', 'ostype', 'category', 'technician_name',
        'technology', 'operator', 'plan_id', 'user_id', 'disponibility_hours',
        'name', 'direction', 'operator_name', 'category_name', 'status_name',
        'phone', 'email', 'document_number', 'service_number',"ID", "sequential_id",
        "plan_brujula", "coordinates", "plan_name")



class CreateOsSerializers(BaseModelSerializer):

    #campos para el plan
    tradename = serializers.CharField(required=False)
    technology = serializers.CharField(required=False)

    #Campos para el cliente
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    document_number = serializers.CharField(required=False)
    direction_text = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    service_number = serializers.CharField(required=False)
    direction = serializers.IntegerField(required=False, write_only=True)
    document_type = serializers.IntegerField(required=False)


    class Meta:
        model = Os
        fields = ('status', 'technician', 'ostype', 'category', 'technology', 
                  'operator', 'plan_id', 'user_id','disponibility_hours','ID',
                  'tradename','first_name','last_name','document_number',
                  'direction_text','phone','email','service_number',
                  'direction','document_type')

        extra_kwargs = {
            'status': {'write_only': True},
            'technician': {'write_only': True},
            'ostype': {'write_only': True},
            'category': {'write_only': True},
            'technology': {'write_only': True},
            'operator': {'write_only': True},
            'plan_id': {'write_only': True},
            'user_id': {'write_only': True},
            'disponibility_hours': {'write_only':True},
            'ID' : {'read_only': True},
        }

    def validate(self, data):
        """
        Debe venir algun dato de usuario y plan
        """
        if 'user_id' not in data and 'first_name' not in data:
            raise serializers.ValidationError("Se debe proveer un campo de usuario")

        if 'plan_id' not in data and 'tradename' not in data:
            raise serializers.ValidationError("Se debe proveer un campo de plan")

        return data


    def create(self, validated_data):

        user_id = validated_data.get('user_id', None)
        plan_id = validated_data.get('plan_id', None)
        data = Os()

        if not user_id: 
            #Crear client en caso de no existir 
            client = Client()
            client.first_name = validated_data.get('first_name')
            client.last_name = validated_data.get('last_name')
            client.document_type = validated_data.get('document_type')
            client.document_number = validated_data.get('document_number')
            client.phone = validated_data.get('phone')
            client.email = validated_data.get('email')
            client.service_number = validated_data.get('service_number')
            if 'direction' in validated_data:
                client.direction = validated_data.get('direction')
            client.direction_text = validated_data.get('direction_text')
            client.operator = validated_data['operator']
            client.save()
            data.user_brujula = client
        else:
            data.user_id = validated_data['user_id']


        if not plan_id:
            #Busca plan y sino lo crea
            plan_name = validated_data.get('tradename').upper()
            
            try:
                plan = OperatorPlans.objects.get(operator=validated_data['operator'],
                                                 tradename=plan_name)
            except Exception as e:
                plan = OperatorPlans.objects.create(operator=validated_data['operator'],
                                                    tradename=plan_name)

                if 'technology' in validated_data:
                    plan.technology = validated_data['technology'].upper()
                    plan.save()

            data.plan_brujula = plan
        else:
            data.plan_id = validated_data['plan_id']


        if 'status' in validated_data:
            data.status = validated_data['status']

        if 'direction' in validated_data:
            data.direction = validated_data.get('direction')
        elif data.user_brujula:
            data.direction = data.user_brujula.direction

        data.technician = validated_data['technician']
        data.ostype = validated_data['ostype']
        data.category = validated_data['category']
        data.technology = validated_data['technology']
        data.operator = validated_data['operator']
        data.disponibility_hours = validated_data['disponibility_hours']
        data.save()
        return data


class OsPicSerializers(BaseModelSerializer):
    photo_base64 = Base64ImageField(write_only=True, required=False)
    photo = serializers.ImageField(required=False)

    def create(self, validated_data):
        if validated_data.get('photo_base64'):
            validated_data['photo'] = validated_data.pop('photo_base64')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('photo_base64'):
            validated_data['photo'] = validated_data.pop('photo_base64')
        return super().update(instance,validated_data)

    class Meta:
        model = OsPic
        fields = '__all__'


class DisplacementSerializers(BaseModelSerializer):
    class Meta:
        model = Displacement
        fields = '__all__'


class TripSummarySerializers(BaseModelSerializer):
    class Meta:
        model = TripSummary
        fields = '__all__'