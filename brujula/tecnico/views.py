import calendar
import json
import locale
from datetime import datetime
from typing import Any, Dict, List, Union

import django_filters

from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.db.models import Model, Count, Q


from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.views import APIView


from userapp.models import UserApp
from utils.models import BaseModel
from utils.permissions import OnlyView
from utils.views import BaseViewSet, MultipleChoicesAPIView
from category.models import Category
from sesionapp.models import HistorySession
from operador.models import Operator
from ostype.models import Ostype
from direction.models import Direction

from .datatables import DisponibilityDatatable, TechnicianDatatable, ScheduleDatatable, AbsenceDatatable, HolidayDatatable, TechnicianCategoriesDatatable
from .serializers import *
from .models import (Technician, TechnicianPic, Schedule, Disponibility, Absence, schedule_status,
    schedule_days, status_tecnicos, documentos, Holiday, absence_status as a_status,absence_type as a_type)




format_allowed = {'png','PNG','jpeg', 'jpg'}

class TechnicianFilter(django_filters.FilterSet):
    class Meta:
        model = Technician
        exclude = ['device']


class TechnicianView(BaseViewSet):
    serializer_class = DetailTechnicianSerializers
    queryset = Technician.objects.all()
    filterset_fields = ('ID','birthday','name', 'last_name', 'operator',
                       'status', 'user', 'id_number', 'id_type', 'categories',
                       'is_supervisor', 'supervised_by')
    # filterset_class = TechnicianFilter
    # filter_backends = []

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            serializer_class = DetailTechnicianSerializers
        else:
            serializer_class = CreateTechnicianSerializers
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_queryset(self):

        if self.request.user.is_superuser:
            qs = Technician.objects.all()
        else:
            qs = Technician.objects.filter(operator=self.request.user.operator)

        if 'supervised_by__none' in self.request.query_params:
            qs = qs.annotate(num=Count('supervised_by')).filter(num=0)

        return qs 

    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(TechnicianDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return TechnicianDatatable(request).get_data()
    
    @action(detail=False, methods=['get'])
    def datatables_categories_struct(self, request) -> JsonResponse:
        return JsonResponse(TechnicianCategoriesDatatable(request).get_struct(), safe=True)
    
    @action(detail=False, methods=['post'])
    def datatables_categories(self, request) -> JsonResponse:
        return TechnicianCategoriesDatatable(request).get_data()
    
    @action(detail=True, methods=['get'])
    def get_full_disponibility(self, request, pk) -> JsonResponse:

        l = list()

        if Schedule.objects.filter(technician=pk).exists():
            m = list()
            n = list()
            schedule = Schedule.objects.get(technician=pk)

            l.append({'scheduleTechnician':schedule.technician.pk,'scheduleeStart': schedule.schedule_start_date,'scheduleEnd': schedule.schedule_end_date})

            disponibility = schedule.disponibility.all()
            absences = schedule.absence.all()

            for item in disponibility:
                m.append({'scheduleStatus':item.schedule_status,'scheduleDay': item.schedule_day,'Direction': item.dir.name,'ScheduleStartDate': item.schedule_start_time,'ScheeduleEndDate': item.schedule_end_time})
            
            for item in absences:
                n.append({'AbsenceStatus':item.status,'AbsenceDay': item.schedule_day,'AbsenceOperator': item.operator.pk,'AbsenceStartTime': item.time_start,'AbsenceEndTime': item.time_end})

            l.append({'Disponibilitys':m})
            l.append({'Absences':n})
        
        else:
            l.append("No hay un horario asociado al tecnico")

        return JsonResponse({'get_full_disponibility':l}, safe=False)
    
    @action(detail=True, methods=['post'])
    def _auth(self,request, pk) ->JsonResponse:
        try:
            email= request.data['email']
            password= request.data['password']

            owner = Technician.objects.get(ID=pk)
            user = UserApp.objects.get(email=owner.user_id.email)
            if user.email == email:

                validate = check_password(password, user.password)
                
                if validate :
                    token, _ = Token.objects.get_or_create(user=owner.user_id)
                    HistorySession.objects.create(
                        user =owner.user_id,
                        ip = request.META['REMOTE_ADDR']
                    )
                    return JsonResponse({'error':False, 'token': token.key })
                else:
                    return JsonResponse({'error': True,'mensaje': "contraseña incorrecta"})

            else:
                return JsonResponse({'error': True,'mensaje': "email incorrecto"})
    
        except Technician.DoesNotExist:
            return JsonResponse({'error': True, 'mensaje': 'Tecnico no registrado'}, status=status.HTTP_404_NOT_FOUND)
    
    #*Función para validar que el tecnico no tenga usuarios supervisados asignados si no es supervisor.
    #? Puede que se termine validando por FrontEnd
    def supervisor_validate(self, request):
        body = json.loads(request.body)
        if not body['is_supervisor'] and body['technicians_supervised'] != None:
            return True
        return False

    def create(self, request, *args, **kwargs):
        # if self.supervisor_validate(request):
        #     return JsonResponse({'error': True, 'mensaje': 'Usuario no es supervisor y tiene usuarios asignados.'},
        #     status=status.HTTP_404_NOT_FOUND)
        return super().create(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def status_history(self, request, pk: int = None) -> JsonResponse:
        """
            
            This function returns Historical changes of instance model

            :param self: Instance of ViewSet
            :type self: ViewSet Class extend of BaseViewSet

            :returns: List of str, this contains fields of Model defined in Viewset
            :rtype: list
        
        """
 
        def get_fields(self: BaseViewSet):

            """
            
                This function returns fields of defined Model in Viewset

                :param self: Instance of ViewSet
                :type self: ViewSet Class extend of BaseViewSet

                :returns: List of str, this contains fields of Model defined in Viewset
                :rtype: list
            
            """

            return [ field.name for field in type(self.queryset[0])._meta.fields]

        def get_first(self: BaseViewSet, instance ):

            """
            
                This function returns fields of defined Model in Viewset

                :param self: Instance of ViewSet
                :type self: ViewSet Class extend of BaseViewSet

                :returns: Dict, this contains first value of instance
                :rtype: dict
            
            """

            def replace_id_pk(value: str) -> str:

                """
            
                    This function returns the 'value' field without '_id' and '_pk' substring

                    :param self: Instance of ViewSet
                    :type self: ViewSet Class extend of BaseViewSet

                    :returns: List of str, this contains fields of Model defined in Viewset
                    :rtype: list
            
                """

                return value.replace('_id','').replace('_pk','')

            #Get fileds of Model defined in ViewSet
            fields: List[str] = get_fields(self)

            #Return dict, contains initial values of instance
            return { replace_id_pk(key):value for key, value in instance.__dict__.items() if (replace_id_pk(key) in fields) and (not (key in self.history_ignore_fields)) }

        def is_related(self: BaseViewSet, field) -> int:

            """
            
                This function returns id of related object to instance of Model

                :param self: Instance of ViewSet
                :type self: ViewSet Class extend of BaseViewSet
                :param field: Field in Model
                :type field: All posible fields in Django Model

                :returns: Int, pk or ID of related object
                :rtype: int
            
            """

            #Get list related models
            related_models: Model = [ related.model for related in type(self.queryset[0])._meta.related_objects] + [User]
            result: int = field

            #If 'field' is 'related_models' search primary key
            if field.__class__ in related_models:

                if hasattr(field, 'ID'):

                    result = field.ID

                elif hasattr(field, 'pk'):

                    result = field.pk

            return result

        def get_text(self, instance_model, change, change_aux):
            if hasattr(instance_model, 'get_text_history'):
                txt = instance_model.get_text_history(change_aux.updater, change, change_aux)
                if txt and change.field == 'status':
                    return txt
            if change.field != 'status':
                the_txt_field = None
            return the_txt_field


        #Get instance of model to get history
        try:
            
            instance_model: BaseModel = self.queryset.get(ID=pk)
            instance_model_history: BaseModel = instance_model.history.all()

            if len(instance_model_history) == 0:
                result: Dict[str, Any] = {
                    'first': {},
                    'changes': [],
                }
                return JsonResponse(result, safe=True)

            #Get first value of instance
            first: Dict[str, Any] = get_first(self, instance_model_history[len(instance_model_history) - 1])


            changes: List[Dict[str, Any]] = []

            
            for index, change in enumerate(instance_model_history[0: len(instance_model_history) - 1], start=0):

                #Get instance of change
                change_aux: BaseModel = change
               
                #Get fields that have changed between 'change' and next change
                fields_changes: Dict[str, Any] = change.diff_against(instance_model_history[index + 1])
                dict_changes: Dict[str, Dict[str, Any]] = {}
                new_dict_changes = []
                
                for change in fields_changes.changes:
                    
                    #Get field that have changed
                    #NOMBRE DEL CAMPO
                    field = change.field

                    #Exclude fields changes
                   
                    if not (field in self.history_ignore_fields):

                        if not change.old:
                            continue
                        
                        #Save Old and New value in fields
                        #CAMPOS

                        the_change = {
                            "field": get_text(self, instance_model, change, change_aux) ,
                            "date":change_aux.history_date.strftime("%d-%m-%Y %H:%M")
                        }

                        if the_change['field'] is not None:
                            new_dict_changes.append(the_change)
                        
                        dict_changes[field]: Dict[str, Any] =   {
                                                    'old_value': is_related(self, change.old),
                                                    'new_value': is_related(self, change.new),
                                                }
                    
                
                #Save user thah have changed instance
                dict_changes['updater']: Dict[str, User] =   {
                                            'old_value': is_related(self, change_aux.updater),
                                            'new_value': is_related(self, change_aux.updater),
                                        }

                #Save datetime that have changed instance
                dict_changes['updated']: Dict[str, datetime] =   {
                                            'old_value': is_related(self, change_aux.history_date),
                                            'new_value': is_related(self, change_aux.history_date),
                                        }

                #Save changes to list of changes
                if new_dict_changes:
                    changes.append(new_dict_changes)

            result: Dict[str, Any] = {
                'first': first,
                'changes': changes,
            }


            return JsonResponse( result, safe=True)
        except Exception as e:
            raise e
            return JsonResponse({"error":True,"mensaje":"dato no existente"})
        


class TechnicianPicView(BaseViewSet):
    serializer_class = TechnicianPicSerializers
    queryset = TechnicianPic.objects.all()
    filter_fields = ['ID','caption','owner_tech','creator','updater','updated','created']

    @action(detail=True, methods=['get'])
    def get_pic(self, request, pk)->JsonResponse:
        
        response = list()
        if TechnicianPic.objects.filter(owner_tech=pk).exists():
            qs= TechnicianPic.objects.all().filter(owner_tech=pk)
            for item in qs:
                response.append({
                    'ID':item.ID,
                    'owner_tech':item.owner_tech.ID,
                    'caption':item.caption,
                    'img':item.photo.url
                    })
            return JsonResponse({'response':response},safe=False)
        else:
            response.append('No existe imagenes asociadas al tecnico')
            return JsonResponse(response, safe=False)

    def create(self, request):
        upload =str(request.FILES)
        tec_type = upload.split('.')[-1].split(' ')[0]

        if not tec_type in format_allowed:
            datos={'Error':True, 'Message':'Formato de imagen no valido.'}
            return JsonResponse(datos, safe=False)

        serializer = TechnicianPicSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return TechnicianPic.objects.all()
        return TechnicianPic.objects.filter(owner_tech__operator=self.request.user.operator)
    
   


class ScheduleView(BaseViewSet):
    serializer_class = ScheduleSerializers
    queryset = Schedule.objects.all()
    filter_fields = ["ID", "schedule_start_date","schedule_end_date",
                     "technician","disponibility","absence",]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return Schedule.objects.filter(technician__operator__ID=o)
            return Schedule.objects.all()

        return Schedule.objects.filter(technician__operator__ID=user.operator)

    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(ScheduleDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return ScheduleDatatable(request).get_data()
    
    @action(detail=False, methods=['get'])
    def get_full(self, request) -> JsonResponse:

        j = list()
        if Schedule.objects.all().exists():
            qs = Schedule.objects.all()
            for schedule in qs:#*Include technician info
                k = list()
                k.append({"ID":schedule.technician.pk, "technician":schedule.technician.name, "start time": schedule.schedule_start_date, "end time": schedule.schedule_end_date})
                disponibilitys =schedule.disponibility.all()
                absences = schedule.absence.all()
                for dispo in disponibilitys:
                    l = list()
                    l.append({"dir": dispo.dir.name, "start time": dispo.schedule_start_time, "end time": dispo.schedule_end_time})
                k.append({"disponibilitys":l})#* Include disponibilitys
                for abse in absences:
                    ñ = list()
                    ñ.append({"operator": abse.operator.name, "Day": abse.schedule_day, "status": abse.status, "start": abse.time_start, "end": abse.time_end })
                k.append({"absences": ñ})#* Include Absences
        j.append(k)
        return JsonResponse({'get_full_disponibility':j}, safe=False)    



class DisponibilityView(BaseViewSet):
    serializer_class = DisponibilitySerializers
    queryset = Disponibility.objects.all()
    filter_fields = ['ID',"schedule_status","schedule_day","dir","schedule_start_time","schedule_end_time"]

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_superuser:
    #         o = self.request.query_params.get('operator')
    #         if o:
    #             return Disponibility.objects.filter(operator=o)
    #         return Disponibility.objects.all()

    #     return Disponibility.objects.filter(operator=user.operator)

    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(DisponibilityDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return DisponibilityDatatable(request).get_data()


class AbsenceView(BaseViewSet):
    serializer_class = AbsenceSerializers
    queryset = Absence.objects.all()
    filter_fields = ['ID', "operator","status","time_start","time_end"]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DetailAbsenceSerializers
        return AbsenceSerializers

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return Absence.objects.filter(operator__ID=o)
            return Absence.objects.all()

        return Absence.objects.filter(operator=user.operator)
    
    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(AbsenceDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return AbsenceDatatable(request).get_data()


class HolidayView(BaseViewSet):
    serializer_class = HolidaySerializers
    queryset = Holiday.objects.all()
    filter_fields = ['ID', "name","day","status"]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return Holiday.objects.filter(operator__ID=o)
            return Holiday.objects.all()

        return Holiday.objects.filter(operator=user.operator)
    
    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(HolidayDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return HolidayDatatable(request).get_data()


class TechnicianFormChoicesList(MultipleChoicesAPIView):
    """
    List all choices for documentos, schedule_status, schedule_days, status_tecnicos
    """
    choices_response = {"documentos": documentos,
                        "schedule_status": schedule_status,
                        "schedule_days": schedule_days,
                        "status_tecnicos": status_tecnicos}     

def am_or_pm(data):

    if int(data) >= 0 and int(data) < 12:
        return 'am'
    elif int(data) >= 12 and int(data) < 24:
        return 'pm' 

        
class AbsenceFinderView(APIView):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Parámetro operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    generic_param = openapi.Parameter('generic', openapi.IN_QUERY, 
    description="Parámetro para hacer la busqueda",
    type=openapi.TYPE_STRING)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Parámetro de técnico para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[operator_param, generic_param, technician_param])
    def get(self, request, *args, **kwargs):

        try:

            locale.setlocale(locale.LC_TIME, "es_CL.utf8")
            operator = request.GET.get('operator', None)
            generic = request.GET.get('generic', None)
            technician = request.GET.get('technician', None)
            list_of_absences = []
            schedule = Schedule.objects.filter(technician=technician, technician__operator=operator)

            for i in schedule:

                absence_list = [abscen for abscen in i.absence.values('ID')]

                if generic is not None and operator is not None:

                    try:

                        number = int(generic)
                        absences = []

                        for item in absence_list:

                            absence = Absence.objects.filter(operator=operator, ID=item['ID']).filter( 
                                                                                                        Q(sequential_id=number)|
                                                                                                        Q(type=number)|
                                                                                                        Q(status=number)|
                                                                                                        Q(time_end__day=number)|
                                                                                                        Q(time_end__month=number)|
                                                                                                        Q(time_end__year=number)|
                                                                                                        Q(time_start__day=number)|
                                                                                                        Q(time_start__month=number)|
                                                                                                        Q(time_start__year=number)|
                                                                                                        Q(time_end__hour=number)|
                                                                                                        Q(time_end__minute=number)|
                                                                                                        Q(time_end__second=number)|
                                                                                                        Q(time_start__hour=number)|
                                                                                                        Q(time_start__minute=number)|
                                                                                                        Q(time_start__second=number)
                                                                                                    )
                            if len(absence) > 0:

                                absences.append(absence)

                        for data in absences:

                            for d in data:
                                
                                text = {
                                            'ID': d.ID,
                                            'created': d.created.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.created.strftime('%H'))),
                                            'updated': d.updated.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.updated.strftime('%H'))),
                                            'deleted': d.deleted,
                                            'sequential_id': d.sequential_id , 
                                            'operator': d.operator.name,
                                            'status': a_status[d.status][1],
                                            'time_start': d.time_start.strftime('%A, %d de %B del %Y desde las %I:%M {}').format(am_or_pm(d.time_start.strftime('%H'))),
                                            'time_end': d.time_end.strftime('%A, %d de %B del %Y hasta las %I:%M {}').format(am_or_pm(d.time_end.strftime('%H'))),
                                            'type': a_type[d.type][1],
                                            'creator': d.creator,
                                            'updater': d.updater
                                        }
                                
                                if text not in list_of_absences:

                                    list_of_absences.append(text)

                    except ValueError:

                        try:

                            date_time = datetime.strptime(generic,'%d-%m-%Y %H:%M:%S')
                            date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
                            absences = []

                            for item in absence_list:

                                absence = Absence.objects.filter(operator=operator,ID=item['ID']).filter( 
                                                                                            Q(time_start=date_time)|
                                                                                            Q(time_end=date_time)
                                                                                        )
                                
                                if len(absence) > 0:

                                    absences.append(absence)

                                for data in absences:

                                    for d in data:

                                        text = {
                                                    'ID': d.ID,
                                                    'created': d.created.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.created.strftime('%H'))),
                                                    'updated': d.updated.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.updated.strftime('%H'))),
                                                    'deleted': d.deleted,
                                                    'sequential_id': d.sequential_id , 
                                                    'operator': d.operator.name,
                                                    'status': a_status[d.status][1],
                                                    'time_start': d.time_start.strftime('%A, %d de %B del %Y desde las %I:%M {}').format(am_or_pm(d.time_start.strftime('%H'))),
                                                    'time_end': d.time_end.strftime('%A, %d de %B del %Y hasta las %I:%M {}').format(am_or_pm(d.time_end.strftime('%H'))),
                                                    'type': a_type[d.type][1],
                                                    'creator': str(d.creator),
                                                    'updater': str(d.updater)
                                                }
                                        
                                        if text not in list_of_absences:

                                            list_of_absences.append(text)

                        except ValueError:

                            try:

                                date_time = datetime.strptime(generic,'%d-%m-%Y')
                                date = date_time.strftime('%Y-%m-%d')
                                absences = []

                                for item in absence_list:

                                    absence = Absence.objects.filter(operator=operator, ID = item['ID']).filter( 
                                                                                                                    Q(time_end__date=date)|
                                                                                                                    Q(time_start__date=date)
                                                                                                                )
                                    
                                    if len(absence) > 0:

                                        absences.append(absence)

                                    for data in absences:

                                        for d in data:

                                            text = {
                                                        'ID': d.ID,
                                                        'created': d.created.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.created.strftime('%H'))),
                                                        'updated': d.updated.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.updated.strftime('%H'))),
                                                        'deleted': d.deleted,
                                                        'sequential_id': d.sequential_id , 
                                                        'operator': d.operator.name,
                                                        'status': a_status[d.status][1],
                                                        'time_start': d.time_start.strftime('%A, %d de %B del %Y desde las %I:%M {}').format(am_or_pm(d.time_start.strftime('%H'))),
                                                        'time_end': d.time_end.strftime('%A, %d de %B del %Y hasta las %I:%M {}').format(am_or_pm(d.time_end.strftime('%H'))),
                                                        'type': a_type[d.type][1],
                                                        'creator': str(d.creator),
                                                        'updater': str(d.updater)
                                                    }
                                            
                                            if text not in list_of_absences:

                                                list_of_absences.append()

                            except ValueError:

                                date_time = datetime.strptime(generic,'%H:%M:%S')
                                time = date_time.strftime('%H:%M:%S')
                                absences = []

                                for item in absence_list:

                                    absence = Absence.objects.filter(operator=operator, ID=item['ID']).filter( 
                                                                                                                Q(time_end__time=time)|
                                                                                                                Q(time_start__time=time)
                                                                                                            )
                                    if len(absence) > 0:

                                        absences.append(absence)

                                    for data in absences:

                                        for d in data:

                                            text = {
                                                        'ID': d.ID,
                                                        'created': d.created.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.created.strftime('%H'))),
                                                        'updated': d.updated.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.updated.strftime('%H'))),
                                                        'deleted': d.deleted,
                                                        'sequential_id': d.sequential_id , 
                                                        'operator': d.operator.name,
                                                        'status': a_status[d.status][1],
                                                        'time_start': d.time_start.strftime('%A, %d de %B del %Y desde las %I:%M {}').format(am_or_pm(d.time_start.strftime('%H'))),
                                                        'time_end': d.time_end.strftime('%A, %d de %B del %Y hasta las %I:%M {}').format(am_or_pm(d.time_end.strftime('%H'))),
                                                        'type': a_type[d.type][1],
                                                        'creator': str(d.creator),
                                                        'updater': str(d.updater)
                                                    }
                                            
                                            if text not in list_of_absences:

                                                list_of_absences.append(text)
                                
                elif operator is not None and generic is None and technician is not None:

                    absences = []

                    for item in absence_list:

                        absence = Absence.objects.filter(operator=operator,ID=item['ID'])

                        if len(absence) > 0:

                            absences.append(absence)

                        for data in absences:

                            for d in data:

                                text = {
                                            'ID': d.ID,
                                            'created': d.created.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.created.strftime('%H'))),
                                            'updated': d.updated.strftime('%d-%m-%Y %I:%M {}').format(am_or_pm(d.updated.strftime('%H'))),
                                            'deleted': d.deleted,
                                            'sequential_id': d.sequential_id , 
                                            'operator': d.operator.name,
                                            'status': a_status[d.status][1],
                                            'time_start': d.time_start.strftime('%A, %d de %B del %Y desde las %I:%M {}').format(am_or_pm(d.time_start.strftime('%H'))),
                                            'time_end': d.time_end.strftime('%A, %d de %B del %Y hasta las %I:%M {}').format(am_or_pm(d.time_end.strftime('%H'))),
                                            'type': a_type[d.type][1],
                                            'creator': str(d.creator),
                                            'updater': str(d.updater)
                                        }
                                
                                if text not in list_of_absences:

                                    list_of_absences.append(text)
                        
                elif ((operator is None and generic is None and technician is None) or 
                      (operator is not None and generic is None and technician is None) or 
                      (operator is None and generic is None and technician is not None) or 
                      (operator is None and generic is not None and technician is None)):

                    raise ValidationError({'message':'No existe un operador para realizar la Búsqueda'})    
                
            return JsonResponse({'wanted_absences': list_of_absences})
            
        except Exception as e:
            
            raise e

class AbsenceCreatorView(APIView):

    day_init_param = openapi.Parameter('initial', openapi.IN_QUERY, 
    description="Parámetro para la fecha inicial",
    type=openapi.TYPE_STRING)

    day_final_param = openapi.Parameter('final', openapi.IN_QUERY, 
    description="Parámetro para la fecha final",
    type=openapi.TYPE_STRING)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Parámetro para el operador",
    type=openapi.TYPE_STRING)

    type_param = openapi.Parameter('type', openapi.IN_QUERY, 
    description="Parámetro para el tipo de permiso",
    type=openapi.TYPE_STRING)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Parámetro para el técnico",
    type=openapi.TYPE_STRING)

    def get(self, request, *args, **kwargs):

        try:

            list_types_of_absences = []

            for data in a_type:

                list_types_of_absences.append({
                                                    'id': data[0],
                                                    'name': data[1]
                                                })
                
            return JsonResponse({'types_of_absences': list_types_of_absences})
        
        except Exception as e:
            
            raise e
    
    @swagger_auto_schema(manual_parameters=[day_init_param, day_final_param])
    def post(self, request, *args, **kwargs):

        try:

            day_initial = request.GET.get('initial',None)
            day_final = request.GET.get('final', None)
            operator = request.GET.get('operator', None)
            technician = request.GET.get('technician', None)
            initial_format = datetime.strptime(day_initial,'%d-%m-%Y')
            final_format = datetime.strptime(day_final,'%d-%m-%Y')
            type = request.GET.get('type', None)

            if (day_initial is not None and 
                day_final is not None and
                operator is not None and 
                technician is not None and 
                type is not None
                ):

                schedule = Schedule.objects.filter( 
                                                    schedule_start_date__lte = initial_format,
                                                    schedule_end_date__gte = final_format,
                                                    technician__operator__ID = operator,
                                                    technician = technician
                                                    )
                
                
                if len(schedule) > 0:

                    absence = Absence.objects.create(
                                                        operator__ID = operator,
                                                        status = 0,
                                                        time_start = initial_format,
                                                        time_end = final_format,
                                                        type = type
                                                    )
                    schedule[0].absence.add(absence)

                    return JsonResponse({'message': 'Ausencia Creada'})
                else:
                    raise ValidationError({'message':'Horario no disponible para la fecha'})
                
            else: 

                raise ValidationError({'message':'Parámetros incompletos para Crear Ausencia'})

        except Exception as e:
            
            raise e

class CreateDisponibilityScheduleView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            request_body = json.loads(request.body.decode('utf-8'))
            id_technician = request_body['technician']
            data = request_body['disponibility']
            start = datetime.strptime(request_body['start_date'], '%d-%m-%Y')
            if 'end_date' in request_body and request_body['end_date'] is not None:
               end =  datetime.strptime(request_body['end_date'], '%d-%m-%Y')
            else:
                end = None
            list_d = []
            if (
                    id_technician is not None and 'technician' in resquest_body and
                    'disponibility' in request_body and data is not None and 
                    'start_date' in request_body and start is not None
               ):
                for item in data:
                    dir = Direction.objects.filter(id=int(item['dir']))
                    d = Disponibility.objects.create(
                                                        schedule_status = 0, 
                                                        schedule_day = item['day'],
                                                        dir = dir[0],
                                                        schedule_start_time = datetime.strptime(item['start'], '%H:%M'),
                                                        schedule_end_time = datetime.strptime(item['end'], '%H:%M')
                                                    )
                    list_d.append(d)
                
                schedule = Schedule.objects.create(
                                                    schedule_start_date = start,
                                                    schedule_end_date = end, 
                                                    technician__ID = request_body['technician']
                                                )
                for d in list_d:
                    schedule.disponibility.add(d)

            else:
                raise ValidationError({'message':'Data de Disponibilidades vacía'})

            return Response({"message": 'Horario Nuevo Creado'}, status=200)

        except Exception as e:
            
            raise e

class ModifyCategoriesInDatatableView(APIView):

    def post(self, request, *args, **kwargs):
        request_body = json.loads(request.body.decode('utf-8'))
        try:
            id_technician = request_body.get('technician', None)
            option = request_body.get('option', None)
            id_category = request_body.get('category', None)

            if id_technician is not None and option is not None:
                technician = Technician.objects.get(ID=id_technician)
                if option == "modificar":
                    if id_category is not None:
                        category = Category.objects.get(ID=id_category)
                        technician.categories.add(category)
                    else:
                        raise ValidationError({'message': 'Parámetro de categoría vacío.'})
                    return Response({'message': 'Categoria agregada con éxito al técnico'}, status=200)
                
                elif option == 'eliminar':
                
                    data = technician.categories.values('ID', 'os_type__ID')
                    for item in data:
                        if item['ID'] == id_category:
                            technician.categories.remove(item['ID'])
                   
                    return Response({'message': 'Categoría eliminada con éxito al técnico'}, status=200)
            else:
                raise ValidationError({'message':'Parámetros incompletos al enviar petición'})

        except Exception as e:
            raise e
