import locale
from rest_framework import serializers
from utils.serializers import BaseModelSerializer
from userapp.models import UserApp
from category.models import Category 
from .models import Technician, TechnicianPic, Schedule, Disponibility, Absence, absence_type as a_type, absence_status as a_status
from .models import Holiday as HModel

__all__ = ['DetailTechnicianSerializers','CreateTechnicianSerializers','TechnicianPicSerializers',
            'ScheduleSerializers','DisponibilitySerializers','AbsenceSerializers','DetailAbsenceSerializers',
            'HolidaySerializers']


class TechnicianPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        #print (kwargs.pop('context', {}).get('request'))
        self.queryset = kwargs.pop('queryset', Technician.objects.all())
        super().__init__(**kwargs)

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset
        return super().get_queryset()


class CreateTechnicianSerializers(BaseModelSerializer):

    supervised = TechnicianPrimaryKeyRelatedField(many=True, required=False, write_only=True)
    password = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    status =serializers.CharField(required=False, default=0)
    categories =serializers.CharField(required=False)

    def create(self, validated_data):
        supervised_by_data = validated_data.pop('supervised', [])
        password = validated_data.pop('password', None)
        email = validated_data.pop('email', None)

        technician = Technician.objects.create(**validated_data)
        
        if email and password:
            user = UserApp.objects.create(
                name=technician.name,
                last_name=technician.last_name,
                email=email
            )
            user.set_password(password)
            technician.user = user
            technician.save()

        for supervised_technician in supervised_by_data:
            supervised_technician.supervised_by.add(technician)

        return technician

    class Meta:
        model = Technician
        fields = '__all__'
        read_only_fields = ['ID', 'supervised_by']



class MiniDetailTechnicianSerializers(BaseModelSerializer):

    class Meta:
        model = Technician
        fields = ('ID','name','last_name','birthday','status','id_number','id_type')


class DetailTechnicianSerializers(BaseModelSerializer):

    #my_supervisees = serializers.SerializerMethodField()
    #my_supervisor  = serializers.SerializerMethodField()

    class Meta:
        model = Technician
        fields = '__all__'


class TechnicianPicSerializers(BaseModelSerializer):
    class Meta:
        model = TechnicianPic
        fields = '__all__'


class ScheduleSerializers(BaseModelSerializer):
    class Meta:
        model = Schedule
        fields = ('schedule_start_date', 'schedule_end_date', 'technician', 'disponibility', 'absence', 'Holiday')


class DisponibilitySerializers(BaseModelSerializer):
    class Meta:
        model = Disponibility
        fields = '__all__'


class AbsenceSerializers(BaseModelSerializer):

    class Meta:
        model = Absence
        fields = '__all__'

def am_or_pm(data):

    if int(data) >= 0 and int(data) < 12:
        return 'am'
    elif int(data) >= 12 and int(data) < 24:
        return 'pm'


class DetailAbsenceSerializers(BaseModelSerializer):

    def to_representation(self, instance):

        locale.setlocale(locale.LC_TIME, "es_CL.utf8")
        data = super().to_representation(instance)

        data['ID'] = instance.ID
        data['created'] = instance.created.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(instance.created.strftime('%H')))
        data['updated'] = instance.updated.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(instance.updated.strftime('%H')))
        data['deleted'] = instance.deleted
        data['sequential_id'] = instance.sequential_id
        data['operator'] = instance.operator.name
        data['status'] = a_status[instance.status][1]
        data['time_start'] = instance.time_start.strftime('%A, %d de %B del %Y desde las %I:%M {}').format(am_or_pm(instance.time_start.strftime('%H')))
        data['time_end'] = instance.time_end.strftime('%A, %d de %B del %Y hasta las %I:%M {}').format(am_or_pm(instance.time_end.strftime('%H')))
        data['type'] = a_type[instance.type][1]
        data['creator'] = str(instance.creator)
        data['updater'] = str(instance.updater)

        return data

    class Meta:
        model = Absence
        fields = (
                    'ID', 
                    'created', 
                    'updated', 
                    'deleted', 
                    'sequential_id', 
                    'operator',
                    'status',
                    'time_start',
                    'time_end',
                    'type',
                    'creator',
                    'updater'
                 )
        read_only_fields = (
                                'ID', 
                                'created', 
                                'updated', 
                                'deleted', 
                                'sequential_id', 
                                'operator',
                                'status',
                                'time_start',
                                'time_end',
                                'type',
                                'creator',
                                'updater'
                            )


class HolidaySerializers(BaseModelSerializer):
    class Meta:
        model = HModel
        fields = '__all__'
