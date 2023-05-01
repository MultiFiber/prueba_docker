import json
import io
import requests
import calendar
import humanize
import datetime as dt
import xlsxwriter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.models import User
from typing import Any, Dict, List, Union
from .models import BaseModel
from django.db.models import Model
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse
from datetime import timedelta,datetime
from utils.views import BaseViewSet, MultipleChoicesAPIView
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from report.report import report
from userapp.models import UserApp
from operador.models import Operator
from tecnico.models import Technician, Disponibility, Schedule, Absence, Holiday, schedule_days as days
from ostype.models import Ostype
from category.models import Category
from direction.models import Direction
from rest_framework.decorators import action
from django.db.models import Count

from datetime import datetime, timedelta
from django.http import HttpResponse

from operator_setting.models import OperatorSetting
from django.db.models import Q

from rest_framework.exceptions import ValidationError

from .serializers import *
from .models import (Client, Os, OsPic, Displacement, TripSummary, status as status_os,
    medio_desplazamiento, OperatorPlans)

from .datatables import OsDatatable, DisplacementDatatable
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from utils.permissions import OnlyView
from tecnico.views_calendar import list_of_hours_method, list_of_technician_availables_method, color_block

format_allowed = {'png','PNG','jpeg', 'jpg'}

def phrase(km, status):
    if km is None and status == 'En Desplazamiento':
        return f"Comienzo de Desplazamiento"
    elif km is not None and status == 'En Desplazamiento':
        return f"Fin de Desplazamiento"
    else: 
        return status

def sumar_hora(hora1,hora2):
    formato = "%H:%M:%S"
    lista = hora2.split(":")
    hora=int(lista[0])
    minuto=int(lista[1])
    segundo=int(lista[2])
    h1 = datetime.strptime(hora1, formato)
    dh = timedelta(hours=hora) 
    dm = timedelta(minutes=minuto)          
    ds = timedelta(seconds=segundo) 
    resultado1 =h1 + ds
    resultado2 = resultado1 + dm
    resultado = resultado2 + dh
    resultado=resultado.strftime(formato)
    return str(resultado)

def restar_hora(hora1,hora2):
    formato = "%H:%M:%S"
    if datetime.strptime(hora1, '%H:%M:%S') < datetime.strptime(hora2, '%H:%M:%S'):
        swap = hora2
        hora2 = hora1
        hora1 = swap
    lista = hora2.split(":")
    hora=int(lista[0])
    minuto=int(lista[1])
    segundo=int(lista[2])
    h1 = datetime.strptime(hora1, formato)
    dh = timedelta(hours=hora) 
    dm = timedelta(minutes=minuto)          
    ds = timedelta(seconds=segundo) 
    resultado1 =h1 - ds
    resultado2 = resultado1 - dm
    resultado = resultado2 - dh
    resultado=resultado.strftime(formato)
    return str(resultado)



class ReportView(TemplateView):
    template_name = 'report.html'

    
class ClientView(BaseViewSet):
    serializer_class = ClientSerializers
    queryset = Client.objects.all()
    filterset_fields = ['ID',"name","last_name","direction","phone","email","dni","service_number"]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        return ClientSerializers
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Client.objects.all()
        return Client.objects.filter(operator=self.request.user.operator)


class OsView(BaseViewSet):
    serializer_class = OsSerializers
    queryset = Os.objects.all()
    filterset_fields = ['ID',"status","technician","ostype","category","technology","operator",
                        "plan_id","user_id","disponibility_hours", "disponibility_hours__date"]

    def get_serializer_class(self):
        #print ("Acción", self.request.action)
        if self.request.method == 'POST':
            #print(self.request.method)
            return CreateOsSerializers
        elif self.request.method == 'GET':
            #print(self.request.method)
            return DetailOsSerializers
        return OsSerializers
    
    def get_queryset(self):
        user = self.request.user

        #print (user.is_superuser, user.technician.is_supervisor)
        if user.is_superuser:
            return Os.objects.all()
        elif hasattr(user, 'technician'):
            if user.technician.is_supervisor:
                _qs =  Os.objects.filter(technician__ID__in=user.technician.supervidados_ids)
                return _qs | Os.objects.filter(technician=user.technician)
            else:
                qs = Os.objects.filter(technician=user.technician)
                return qs
                
        return Os.objects.filter(operator=user.operator)

    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(OsDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return OsDatatable(request).get_data()

    @action(detail=True, methods=['get'])
    def valid_status(self, request, pk=None) -> JsonResponse:

        status_allowed = [
            [1, 2, 3, 4],   #Agendada -> Desplazamiento, atendimiento, pausada, en espera
            [2, 3, 4],                        #Desplazamiento -> atendimiento, pausada, en espera
            [3, 6, 8],                   #atendimiento -> pausada, no se pudo instalar, finalizada
            [1, 2, 5, 7],                #pausada -> desplazamiento, cancelada, por reagendar
            [2, 3, 7],                    #en espera -> atendimiento, pausada, por reagendar
            [],                                    #cancelada -> no se cambia
            [],                                    #no se pudo instalar -> no se cambia
            [],                                    #reagendar -> no se cambia
            [],                                    #finalizada -> no se cambia
        ]

        def get_changes(list_ids):
            data = []
            for item in status_os:
                if len(list_ids)> 0 and item[0] in list_ids:
                    data.append({"name":item[1], "value":item[0]})
            return data

        qs = Os.objects.get(ID=pk).status
        return Response({'status': get_changes(status_allowed[qs])}, status=200)

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
    
    @action(detail=True, methods=['get'])
    def oraculo_history(self, request, pk: int = None) -> JsonResponse:

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
                if txt:
                    return txt

            the_old_field = is_related(self, change.old)
            the_new_field = is_related(self, change.new)
            the_txt_field = f"{change_aux.updater} modifico el campo {change.field} de {the_old_field} a {the_new_field}"
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
                            "field": get_text(self, instance_model, change, change_aux),
                            "date":change_aux.history_date.strftime("%d-%m-%Y %H:%M")
                        }
                        
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



class OsPicView(BaseViewSet):
    serializer_class = OsPicSerializers
    queryset = OsPic.objects.all()
    filter_fields = ('caption','owner_os','creator','updater','updated','created')
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @action(detail=True, methods=['get'])
    def get_pic(self, request, pk=None)->JsonResponse:
        
        response = list()
        if OsPic.objects.filter(owner_os__ID=pk).exists():
            qs= OsPic.objects.filter(owner_os__ID=pk, deleted=False)
            for item in qs:
                response.append({
                    'ID':item.ID,
                    'owner_os':item.owner_os.ID,
                    'caption':item.caption,
                    'img':item.photo.url,
                    'user':item.creator.name if item.creator else "",
                    'created':item.created.strftime("%d-%m-%Y %H:%M")
                })
            return Response({'response':response},status=200)
        else:
            response.append('No existe imagenes asociadas a la orden de servicio')
            return Response(response, status=404)
    
    def create(self, request):
        upload =str(request.FILES)
        pic_type = upload.split('.')[-1].split(' ')[0]

        #Temporal por base64
        if False:
            if not pic_type in format_allowed:
                datos={'Error':True, 'Message':'Formato de imagen no valido.'}
                return JsonResponse(datos, safe=False)

        serializer = OsPicSerializers(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return OsPic.objects.filter(owner_os__operator__ID=o)
            return OsPic.objects.all()

        return OsPic.objects.filter(owner_os__operator=user.operator)


class DisplacementView(BaseViewSet):
    serializer_class = DisplacementSerializers
    queryset = Displacement.objects.all()
    filter_fields = ['ID', 'created', 'os']
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return Displacement.objects.filter(owner_os__operator__ID=o)
            return Displacement.objects.all()

        return Displacement.objects.filter(os__operator=user.operator)


    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(DisplacementDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return DisplacementDatatable(request).get_data()

class DashboardView(BaseViewSet):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    inicio_fecha_param = openapi.Parameter('inicio_fecha', openapi.IN_QUERY, 
    description="Fecha inicial para hacer la busqueda",
    type=openapi.TYPE_STRING)

    fin_fecha_param = openapi.Parameter('fin_fecha', openapi.IN_QUERY, 
    description="Fecha final para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @action(detail=False, methods=['get'])
    def get(self, request) -> JsonResponse:
        operator = request.GET.get('operator')
        inicio_fecha = request.GET.get('inicio_fecha', None)
        fin_fecha= request.GET.get('fin_fecha', None)
        today =datetime.now().date()

        if inicio_fecha == None:
            inicio_fecha = today.strftime('%Y-%m-%d')
        else:
            inicio_fecha = datetime.strptime(inicio_fecha,'%Y-%m-%d')
        if fin_fecha == None:
            fin_fecha = datetime.now() + timedelta(days=1)
        else:
            fin_fecha = datetime.strptime(fin_fecha,'%Y-%m-%d')

        if str(inicio_fecha)>str(fin_fecha):
                raise ValidationError({'message': 'La fecha final no puede ser menor que la de inicio'})

        x = Os.objects.values("status").annotate(Count("ID"))
        y = Os.objects.values("ostype").annotate(Count("ID"))
        os = Os.objects.filter(created__gte=inicio_fecha, created__lte=fin_fecha,operator=operator).select_related('technician', 'disponibility_hours').values("technician__ID", "disponibility_hours__dir__name")
        total = Os.objects.all().count()
        status = {'Finalizada': 0, 'En Atendimiento': 0}
        ostype = {}
        dict_zone = {}

        for item in x:
            if item['status'] == 0:
                status["Agendada"]=item['ID__count']
            if item['status'] == 1:
                status["En Desplazamiento"]=item['ID__count']
            if item['status'] == 2:
                status["En Atendimiento"]=item['ID__count']
            if item['status'] == 3:
                status["Pausada"]=item['ID__count']
            if item['status'] == 4:
                status["En Espera Del Cliente"]=item['ID__count']
            if item['status'] == 5:
                status["Cancelada"]=item['ID__count']
            if item['status'] == 6:
                status["No Se Pudo Instalar"]=item['ID__count']
            if item['status'] == 7:
                status["Por Reagendar"]=item['ID__count']
            if item['status'] == 8:
                status["Finalizada"]=item['ID__count']
        
        for item in y:
            if item['ostype'] == 0:
                ostype["Agendada"]=item['ID__count']
            if item['ostype'] == 1:
                ostype["Visita Técnica Cliente Sin Servicio"]=item['ID__count']
            if item['ostype'] == 2:
                ostype["Visita Técnica Cliente Con Servicio"]=item['ID__count']
            if item['ostype'] == 3:
                ostype["Migración"]=item['ID__count']
            if item['ostype'] == 4:
                ostype["Instalación"]=item['ID__count']
            if item['ostype'] == 5:
                ostype["Retiro De Equipo"]=item['ID__count']
            if item['ostype'] == 6:
                ostype["Traslado De Servicio"]=item['ID__count']
        
        for data in os:
            if data['disponibility_hours__dir__name'] in dict_zone:
                if [data['technician__ID']] not in dict_zone[data['disponibility_hours__dir__name']]:
                    dict_zone[data['disponibility_hours__dir__name']].append(data['technician__ID'])
            else: 
                dict_zone[data['disponibility_hours__dir__name']] = [data['technician__ID']]
        for data in dict_zone.keys():
            dict_zone[data] = len(dict_zone[data])

        porcentaje_atendimientos=0
        porcentaje_atendimientos = round((status['En Atendimiento']/total)*100, 2)
        porcentaje_finalizadas = 0
        porcentaje_finalizadas = round((status['Finalizada']/total)*100, 2)

        def get_list_status_changes_OS():
            updates=[]
            changes = Os.history.filter(updated__gte=inicio_fecha, updated__lte=fin_fecha).values('updated','status','history_id', 'category__name', 'technician__name', 'technician__last_name', 'technician__user__email')

            for data in changes:
                updates.append({
                    'updated': data['updated'].strftime('%d-%m-%Y %H:%M:%S'),
                    'category_name': data['category__name'],
                    'technician_name': data['technician__name'],
                    'technician_last_name': data['technician__last_name'],
                    'status_os': status_os[data['status']][1],
                    'user_name': data['technician__user__email'],
                })
            return updates

        return Response({"status":status,
                             "ostype":ostype,
                             "total_os_creadas": total,
                             "porcentaje_finalizadas":porcentaje_finalizadas,
                             "porcentaje_atendimientos": porcentaje_atendimientos,
                             "listado_tecnicos_por_zona": dict_zone,
                             "actividad_reciente_tecnicos": get_list_status_changes_OS(),
                             "total_tecnicos_activos": Technician.objects.filter(operator=operator, status=0).count(),
                             "total_tecnicos_inactivos": Technician.objects.filter(operator=operator).filter(Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4)).count()   ,
                             }, status=200)



class PDFDashboardView(APIView):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[operator_param])
    def get(self, request, *args, **kwargs):
        try:
            operator = request.GET.get('operator')
            op = Operator.objects.get(ID=operator)

            dashboard_response = DashboardView()
            for item in dashboard_response.get(request):
                data = json.loads(item)

            total_agendadas_list = []
            total_canceladas_list = []
            total_finalizadas_list = []
            total_atendimientos_list = []
            for item in data['status']:
                if str(item) == 'Agendada':
                    total_agendadas_list.append({
                                    'value': str(data['status'][item])
                                })
                elif str(item) == 'Finalizada':
                    total_finalizadas_list.append({
                                    'value': str(data['status'][item])
                                })
                elif str(item) == 'Cancelada':
                    total_canceladas_list.append({
                                    'value': str(data['status'][item])
                                })
                elif str(item) == 'En Atendimiento':
                    total_atendimientos_list.append({
                                    'value': str(data['status'][item])
                                })
                    
            if len(total_agendadas_list)<1:
                total_agendadas_list.append({
                    'name': 'Ninguno',
                    'value': str(0),
                })
            if len(total_finalizadas_list)<1:
                total_finalizadas_list.append({
                    'value': str(0),
                })
            if len(total_canceladas_list)<1:
                total_canceladas_list.append({
                    'value': str(0),
                })
            if len(total_atendimientos_list)<1:
                total_atendimientos_list.append({
                    'value': str(0),
                })
            finalizadas_en_curso_list = [{
                'en_curso': str(total_agendadas_list[0]['value']),
                'finalizadas': str(total_finalizadas_list[0]['value']),
            }]
            
            total_os_list = []
            total_os_list.append({
                'value': str(data['total_os_creadas'])
            })

            porcentj_finalizadas_list = []
            porcentj_finalizadas_list.append({
                'value': str(data['porcentaje_finalizadas'])
            })
            porcentj_atendimientos_list = []
            porcentj_atendimientos_list.append({
                'value': str(data['porcentaje_atendimientos'])
            })

            ostype_list = []
            for i in data['ostype']:
                    ostype_list.append({
                        'name':i,
                        'value':str(data['ostype'][i]),
                        'prctj': str(round((data['ostype'][i]/data['total_os_creadas'])*100, 2))
                    })
            if len(ostype_list)<1:
                    ostype_list.append({
                        'name': 'Ninguno',
                        'value': '0',
                        'prctj': '0.0'
                    })

            count_technicians = Technician.objects.filter(operator=operator).count()
            zone_list = []
            for i in data['listado_tecnicos_por_zona']:
                zone_list.append({
                    'direction':i,
                    'cant':data['listado_tecnicos_por_zona'][i],
                    'prctj': str(round((data['listado_tecnicos_por_zona'][i]/count_technicians)*100, 2))
                    })
            if len(zone_list)<1:
                    zone_list.append({
                        'direction': 'Ninguno',
                        'cant': 0,
                        'prctj': str(0.0)
                    })
            act_list = []
            for i in data['actividad_reciente_tecnicos']:
                    act_list.append({   'updated': data['actividad_reciente_tecnicos'][i]['updated'],
                                        'category_name': data['actividad_reciente_tecnicos'][i]['category_name'],
                                        'technician_name': data['actividad_reciente_tecnicos'][i]['technician_name'],
                                        'technician_last_name': data['actividad_reciente_tecnicos'][i]['technician_last_name'],
                                        'status_os': data['actividad_reciente_tecnicos'][i]['status_os'],
                                        'user_name': data['actividad_reciente_tecnicos'][i]['user_name']
                                        })
            information_list = []
            date = datetime.now()
            direction = Direction.objects.get(id=op.country.id)
            op_name = str(op.name).upper()
            information_list.append({
                'fecha_hora': date.strftime('%d-%m-%Y  %H:%M:%S'),
                'direction': f"{direction.name} ISO: {direction.iso}",
                'operator': op_name,
                'email': str(op.email),
                'rut': str(op.operator_code)})

            technicians_list = []
            technicians_list.append({
                'activate': str(round((data['total_tecnicos_activos']/count_technicians)*100, 2)),
                'deactivate': str(round((data['total_tecnicos_inactivos']/count_technicians)*100, 2))
            })

            data = {
                    'ostype': ostype_list,
                    'zone': zone_list,
                    'activity': act_list,
                    'information': information_list,
                    'total_os': total_os_list,
                    'pctj_atendimientos': porcentj_atendimientos_list,
                    'pctj_finalizadas': porcentj_finalizadas_list,
                    'technicians': technicians_list,
                    'agendadas': total_agendadas_list,
                    'finalizadas': total_finalizadas_list,
                    'canceladas': total_canceladas_list,
                    'atendimientos': total_atendimientos_list,
                    'finalizada_en_curso': finalizadas_en_curso_list

                }

            return report(request, 'dashboard', data)
        except Exception as e:
            raise e



class OsFormChoicesList(MultipleChoicesAPIView):
    """
    List all choices for status, medio_desplazamiento
    """
    choices_response = {"status_os": status_os,
                        "medio_desplazamiento": medio_desplazamiento}

def to_seconds(hora):
    formato = "%H:%M:%S"
    hora = hora.strftime(formato)
    lista = hora.split(":")
    hh=int(lista[0])*3600
    mm=int(lista[1])*60
    ss=int(lista[2])
    suma = hh + mm + ss
    return suma

def to_hh_mm_ss(segundos):
    hor = (segundos / 3600)
    min = ((segundos - hor * 3600) / 60)
    seg = segundos - (hor * 3600 + min * 60) 
    if hor < 10:
        hor = f'0{int(hor)}'
    else:
        hor = f'{int(hor)}'
    if min < 10:
        min = f'0{int(min)}'
    else:
        min = f'{int(min)}'
    if seg < 10:
        seg = f'0{int(seg)}'
    else:
        seg = f'{int(seg)}'
    return f"{hor}:{min}:{seg}"


class StartAndFinishRerouteView(APIView):

    def post(self, request):
        request_body = json.loads(request.body.decode('utf-8'))
        try:
            os = Os.objects.get(ID=request_body['os'])
            now = datetime.now()
            if os.status == 0 and (request_body['status'] == 1 or 
                                   request_body['status'] == 2 or 
                                   request_body['status'] == 3): #inicializar desplazamiento
                status = os.status
                os.status = request_body['status']
                os.save()
                if request_body['status'] == 1: #desplazamiento
                    dir1 = Direction.objects.filter(name = request_body['dir1'][0], coordinates__latitude = request_body['dir1'][1], coordinates__longitude = request_body['dir1'][2])
                    if len(dir1) == 0:
                        dir1 = Direction(
                                                    name = f"{request_body['dir1'][0]} - ({request_body['dir1'][1]},{request_body['dir1'][2]})",
                                                    dirtype = 0,
                                                    coordinates = {"latitude": f"{request_body['dir1'][1]}", "longitude": f"{request_body['dir1'][2]}"}, 
                                                    full_direction = f"{request_body['dir1'][0]}, '{request_body['dir1'][1]},{request_body['dir1'][2]}'"
                                                )
                        dir1.save()
                    else:
                        dir1 = dir1[0]
                    dir2 = Direction.objects.filter(name = request_body['dir2'], coordinates__latitude = request_body['dir2'][1], coordinates__longitude = request_body['dir2'][2])
                    if len(dir2) == 0:
                        dir2 =  Direction(
                                                    name = f"{request_body['dir2'][0]} - ({request_body['dir2'][1]},{request_body['dir2'][2]})",
                                                    dirtype = 0,
                                                    coordinates = {"latitude": f"{request_body['dir2'][1]}", "longitude": f"{request_body['dir2'][2]}"},
                                                    full_direction = f"{request_body['dir2'][0]}, '{request_body['dir2'][1]},{request_body['dir2'][2]}'"
                                                )
                                                
                        dir2.save()
                    else:
                        dir2 = dir2[0]
                    displacement = Displacement.objects.create(date=datetime.strftime(now,'%d-%m-%Y'),
                                                               direction_init = dir1,
                                                               direction_final = dir2,
                                                               km_init = request_body['km_init'],
                                                               km_final = None,
                                                               os = os,
                                                               medio_desplazamiento = request_body['medio_desplazamiento'])
                    TripSummary.objects.create(technician=os.technician,
                                               date=datetime.strftime(now,'%d-%m-%Y'),
                                               time=datetime.strftime(now,'%H:%M:%S'),
                                               nro_os=os,
                                               nro_displacement=displacement,
                                               status_init=status,
                                               status_final=os.status,
                                               km_final=None,
                                               km_initial=displacement.km_init)
                    return JsonResponse({'message':f"Desplazamiento creado ID : {displacement.ID} y cambio de Status {status} a {os.status} "})
                return JsonResponse({'message':'Cambio de Status realizado'})
            elif os.status == 1: #finalizar desplazamiento
                km = request_body.get('km_final', None)
                time = request_body.get('time', None)
                if 'km_final' in request_body and request_body['km_final'] == 0:
                    raise ValidationError({'message': "Km final debe ser mayor a 0"})
                if (km is not None) and (time is not None) and (request_body['km_final'] > 0):#colocar en campo correspondiente del modelo el km final y el tiempo de desplazamiento
                    km = float(km)
                    horas = int(int(time) / 3600)
                    num = time / 3600
                    minutos = (num - horas) * 60
                    segundos = (minutos - int(minutos)) * 60
                    if horas < 10:
                        horas = f"0{int(horas)}"
                    else: 
                        horas = f"{int(horas)}"
                    if int(minutos) < 10:
                        minutos = f"0{int(minutos)}"
                    else: 
                        minutos = f"{int(minutos)}"
                    if int(segundos) < 10:
                        segundos = f"0{int(segundos)}"
                    else: 
                        segundos = f"{int(segundos)}"
                    time = horas + ":" + minutos + ":" + segundos
                    displacement = Displacement.objects.filter(os=request_body['os'])
                    lon = len(displacement)
                    if lon > 1:
                        displacement = displacement[lon-1]
                    elif lon == 1:
                        displacement = displacement[0]
                    elif lon == 0:
                        raise ValidationError({'message': "No existen desplazamientos asociados"})
                    if lon > 0:
                        displacement.displacement_time = time
                        displacement.km_final = km
                        displacement.save()  
                        
                        TripSummary.objects.create(technician=os.technician,
                                                date=datetime.strftime(now,'%d-%m-%Y'),
                                                time=datetime.strftime(now,'%H:%M:%S'),
                                                nro_os=os,
                                                nro_displacement=displacement,
                                                status_init=None,
                                                status_final=None,
                                                km_final=displacement.km_final,
                                                km_initial=displacement.km_init)
                    return JsonResponse({'date': displacement.date,
                                         'direction_init': displacement.direction_init.name,
                                         'direction_final': displacement.direction_final.name,
                                         'km_init': displacement.km_init,
                                         'km_final': displacement.km_final,
                                         'medio_desplazamiento':medio_desplazamiento[displacement.medio_desplazamiento][1],
                                         'displacement_time': displacement.displacement_time})
                elif 'status' in request_body and (request_body['status'] == 1):
                    displacement = Displacement.objects.filter(os=request_body['os'])
                    lon = len(displacement)
                    if lon > 1:
                        displacement = displacement[lon-1]
                    elif lon == 1:
                        displacement = displacement[0]
                    elif lon == 0:
                        raise ValidationError({'message': "No existen desplazamientos asociados"})

                    return JsonResponse({'date': displacement.date,
                                         'direction_init': displacement.direction_init.name,
                                         'direction_final': displacement.direction_final.name,
                                         'km_init': displacement.km_init,
                                         'km_final': displacement.km_final,
                                         'medio_desplazamiento':medio_desplazamiento[displacement.medio_desplazamiento][1],
                                         'displacement_time': displacement.displacement_time})

                elif 'status' in request_body and (request_body['status'] == 2 or 
                                                   request_body['status'] == 3 or          
                                                   request_body['status'] == 4): #cambio de status inicial al terminar desplazamiento
                    displacement = Displacement.objects.filter(os=request_body['os'])
                    lon = len(displacement)
                    displacement = displacement[lon-1]
                    status = os.status
                    os.status = int(request_body['status'])
                    os.save()
                    TripSummary.objects.create(technician=os.technician,
                                               date=datetime.strftime(now,'%d-%m-%Y'),
                                               time=datetime.strftime(now,'%H:%M:%S'),
                                               nro_os=os,
                                               nro_displacement=displacement,
                                               status_init=int(status),
                                               status_final=os.status,
                                               km_initial=None,
                                               km_final=None,)
                    return JsonResponse({'message': f"Cambio de status {status} a {os.status}"})
            elif os.status != 0 or os.status != 1: #cambio de status cuando el inicial es distinto de 0 y 1
                displacement = Displacement.objects.filter(os=request_body['os'])
                lon = len(displacement)
                if lon > 1:
                        displacement = displacement[lon-1]
                elif lon == 1:
                    displacement = displacement[0]
                elif lon == 0:
                    raise ValidationError({'message': "No existen desplazamientos asociados"})
                if lon > 0:
                    status = os.status
                    os.status = request_body['status']
                    os.save()
                    TripSummary.objects.create( technician=os.technician,
                                                date=datetime.strftime(now,'%d-%m-%Y'),
                                                time=datetime.strftime(now,'%H:%M:%S'),
                                                nro_os=os,
                                                nro_displacement=displacement,
                                                status_init=status,
                                                status_final=os.status,
                                                km_final=None,
                                                km_initial=None)
                return JsonResponse({'message': f"Cambio de status {status} a {os.status}"})    
        except Exception as e:
            raise e
    
    
class TripSummaryView(APIView):

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="ID de técnico para hacer la busqueda",
    type=openapi.TYPE_STRING)

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[day_param, technician_param])
    def get(self, request, *args, **kwargs):

        try:
            technician = request.GET.get('technician')
            day = request.GET.get('day')
            day_format = datetime.strptime(day, '%d-%m-%Y')
            now = datetime.now()
            now = datetime.strftime(now, '%Y-%m-%d')
            records = TripSummary.objects.filter(technician=technician, date=day_format)

            if len(records) == 0:
                raise ObjectDoesNotExist({'message': 'Técnico O Fecha no existen'})
           
            history_of_changes = []
            km_total = 0
            time_total = '00:00:00'
            time_out = '00:00:00'
            for item in records:
                if item.status_init is not None and item.status_final is not None: 
                    technician = Technician.objects.get(ID=item.technician.ID)
                    settings = OperatorSetting.objects.get(operator=technician.operator)
                    peticion = requests.get(settings.config['operator_user_id_url'] + str(item.nro_os.user_id),
                                            headers={"Authorization":f"{settings.config['operator_authorization_token']}"})
                
                    if peticion.status_code == 200:
                        if len(peticion.json()) > 0:
                            try:
                                client = peticion.json()['first_name'] + " " + peticion.json()['last_name']
                            except KeyError:
                                client = peticion.json()['name'] + " " + peticion.json()['last_name']
                        else:
                            client = ""
                    else:
                        client = ""
                            
                    history_of_changes.append({
                                                'date': f"{item.date.strftime('%d-%m-%Y')} {item.time.strftime('%H:%M:%S')}",
                                                'change': f"{str(item.technician.user)} {phrase(item.km_final,status_os[item.status_final][1])} Orden de Servicio #{item.nro_os.ID} Titular {client}"
                                            })
                    if item.km_initial is not None and item.km_final is not None:
                        km_diff = (item.km_initial-item.km_final)
                        if  km_diff < 0:
                            km_diff = km_diff * (-1)
                        km_total = km_total + km_diff
                        if item.km_final > 0:
                            time = item.nro_displacement.displacement_time
                            if time is not None:
                                time_displacement = time.strftime('%H:%M:%S') 
                                time_total = sumar_hora(time_total, time_displacement)
                                history_of_changes.append(
                                                            {
                                                                'date': f"{item.date.strftime('%d-%m-%Y')} {item.time.strftime('%H:%M:%S')}",
                                                                'change': f"{str(item.technician.user)} colocó el km inicial del desplazamiento en {item.km_initial}"
                                                            }
                                                        )
                                history_of_changes.append(
                                                            {
                                                                'date': f"{item.date.strftime('%d-%m-%Y')} {item.time.strftime('%H:%M:%S')}",
                                                                'change': f"{str(item.technician.user)} colocó el km final del desplazameinto en {item.km_final}"
                                                            }
                                                        )
                elif (item.km_initial is not None and item.km_final is not None) and (item.status_init is None and item.status_final is None):
                    km_diff = (item.km_initial-item.km_final)
                    if  km_diff < 0:
                        km_diff = km_diff * (-1)
                    km_total = km_total + km_diff
                    if item.km_final > 0:
                        time = item.nro_displacement.displacement_time
                        if time is not None:
                            time_displacement = time.strftime('%H:%M:%S')
                            time_total = sumar_hora(time_total,time_displacement)
            
            list_records = records.values_list('time')
            count = 0

            while count < len(list_records)-1:
                hora_a = list_records[count][0]
                if hora_a is not None:
                    hora_a = hora_a.strftime('%H:%M:%S')
                    hora_b = list_records[count+1][0]
                    if hora_b is not None:
                        hora_b = hora_b.strftime('%H:%M:%S')
                        resta = restar_hora(hora_a,hora_b)
                        time_out = sumar_hora(time_out,resta)
                count = count + 1
            
            if len(history_of_changes) > 0:
                return JsonResponse({'distance_traveled':km_total,'route_time':time_total,'idle_time':time_out,'changes': history_of_changes})
            else:
                raise ObjectDoesNotExist({'message': 'No existen trayectos en esta fecha para este técnico'})
        except Exception as e:
            raise e


class JourneysTraveledView(APIView):

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="ID de técnico para hacer la busqueda",
    type=openapi.TYPE_STRING)

    generic_param = openapi.Parameter('generic', openapi.IN_QUERY, 
    description="Parámetro para hacer la busqueda",
    type=openapi.TYPE_STRING)

    def get(self, request, *args, **kwargs):
        try:
            technician = request.GET.get('technician')
            generic = request.GET.get('generic')
            list_of_journeys = []
            if technician is not None and (generic is None):
                displacement = Displacement.objects.filter(os__technician=technician)
                for data in displacement:
                    if data.km_final is not None:
                        day_a = data.date
                        day = day_a.strftime('%d-%m-%Y')
                        time = day_a.strftime('%H:%S:%M')
                        list_of_journeys.append({'date': day, 
                                                'time': time,
                                                'km': data.km_final,
                                                'direction_a': data.direction_init.name,
                                                'direction_b': data.direction_final.name,
                                                'service_number': data.sequential_id,
                                                'id_os': data.os.ID,
                                                'displacement_time': data.displacement_time
                                                }) 
            elif technician is not None and (generic is not None):
                try:
                    number = int(generic)
                    trip_summary = TripSummary.objects.filter(technician=technician).filter(Q(nro_os=number)|Q(km_final=number)|Q(nro_displacement__sequential_id=number))
                    for data in trip_summary:
                        if data.km_final is not None:
                            list_of_journeys.append({'date': data.date.strftime('%d-%m-%Y'), 
                                                    'time': data.time,
                                                    'km': data.km_final,
                                                    'direction_a': data.nro_displacement.direction_init.name,
                                                    'direction_b': data.nro_displacement.direction_final.name,
                                                    'service_number': data.nro_displacement.sequential_id,
                                                    'id_os': data.nro_os.ID,
                                                    'displacement_time': data.nro_displacement.displacement_time
                                                })
                except ValueError:
                    try:
                        day = datetime.strptime(generic,'%d-%m-%Y')
                        trip_summary = TripSummary.objects.filter(technician=technician).filter(date=day)
                        for data in trip_summary:
                            if data.km_final is not None:
                                list_of_journeys.append({'date': data.date.strftime('%d-%m-%Y'), 
                                                        'time': data.time,
                                                        'km': data.km_final,
                                                        'direction_a': data.nro_displacement.direction_init.name,
                                                        'direction_b': data.nro_displacement.direction_final.name,
                                                        'service_number': data.nro_displacement.sequential_id,
                                                        'id_os': data.nro_os.ID,
                                                        'displacement_time': data.nro_displacement.displacement_time
                                                    })
                            
                    except ValueError:
                        direction = generic
                        trip_summary = TripSummary.objects.filter(technician=technician).filter(Q(nro_displacement__direction_init__name__icontains=direction)|Q(nro_displacement__direction_final__name__icontains=direction) )
                        for data in trip_summary:
                            if data.km_final is not None:
                                list_of_journeys.append({'date': data.date.strftime('%d-%m-%Y'), 
                                                        'time': data.time,
                                                        'km': data.km_final,
                                                        'direction_a': data.nro_displacement.direction_init.name,
                                                        'direction_b': data.nro_displacement.direction_final.name,
                                                        'service_number': data.nro_displacement.sequential_id,
                                                        'id_os': data.nro_os.ID,
                                                        'displacement_time': data.nro_displacement.displacement_time
                                                    })
            elif technician is None:
                return ValidationError({'message': 'No existe se proporcionó técnico para realizar la búsqueda'})    
            return JsonResponse({'journeys_traveled': list_of_journeys})
        
        except Exception as e:
            raise e


class PDFRouteReportView(APIView):
    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="ID de técnico para hacer la busqueda",
    type=openapi.TYPE_STRING)

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha para hacer la busqueda",
    type=openapi.TYPE_STRING)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[day_param, technician_param, operator_param])
    def get(self, request, *args, **kwargs):
        try:
            technician = request.GET.get('technician')
            day = request.GET.get('day')
            operator = request.GET.get('operator')
            op = Operator.objects.get(ID=operator)
            trip_summary_response = TripSummaryView(day_param=day,technician_param=technician)
            for item in trip_summary_response.get(request):
                data = json.loads(item)
            changes = data['changes']
            technician = Technician.objects.get(ID=technician)

            information_list = []
            date = datetime.now()
            direction = Direction.objects.get(id=op.country.id)
            op_name = str(op.name).upper()
            information_list.append({
                'fecha_hora': date.strftime('%d-%m-%Y  %H:%M:%S'),
                'direction': f"{direction.name} ISO: {direction.iso}",
                'operator': op_name,
                'email': str(op.email),
                'rut': str(op.operator_code)})

            technician_list = []
            technician_list.append({
                'name': f"{technician.name} {technician.last_name}",
                'user': str(technician.user.email),
                'day': day,
            })

            route_information_list = []
            route_information_list.append({
                'distance_traveled': str(data['distance_traveled']),
                'idle_time': str(datetime.strptime(data['idle_time'], '%H:%M:%S').strftime('%H h %M min')),
                'route_time': str(datetime.strptime(data['route_time'], '%H:%M:%S').strftime('%H h %M min'))
            })

            changes_list = []
            for data in changes:
                
                changes_list.append({
                    'date': str(data['date']),
                    'time': str(data['time']),
                    'user': str(data['change'][0]['user']),
                    'status': str(data['change'][1]['status']),
                    'phrase': str(data['change'][2]['phrase']),
                    'id': str(data['change'][3]['id']),
                    'titular': str(data['change'][4]['titular']),
                })

            data = {
                'information': information_list,
                'technician': technician_list,
                'route_information': route_information_list,
                'changes': changes_list,
            }
            return report(request, 'rute', data)
        
        except Exception as e:
            raise e


class ExcelRouteReportView(APIView):

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="ID de técnico para hacer la busqueda",
    type=openapi.TYPE_STRING)

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[day_param, technician_param])
    def get(self, request, *args, **kwargs):
        try:
            technician = request.GET.get('technician')
            day = request.GET.get('day')
            output = io.BytesIO()
            trip_summary_response = TripSummaryView(day_param=day,technician_param=technician)
            for item in trip_summary_response.get(request):
                data = json.loads(item)
            changes=data['changes']
            technician = Technician.objects.get(ID=technician)
            archivo = xlsxwriter.Workbook(output)
            hoja = archivo.add_worksheet()
            hoja.set_column('B:D', 12)
            
            merge_format_a = archivo.add_format({
                'bold': 2,
                'border': 1,
                'font_size': 16,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': 'black',
                'color': 'white'})
            
            merge_format_b = archivo.add_format({
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': 'white'})

            merge_format_c = archivo.add_format({
                'border': 1,
                'font_size': 12,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': 'yellow'})

            merge_format_d = archivo.add_format({
                'border': 1,
                'font_size': 12,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': 'black',
                'color': 'white'})

            merge_format_e = archivo.add_format({
                'bold': 1,
                'border': 1,
                'font_size': 13,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': 'black',
                'color': 'white'})
            

            date = datetime.now()

            hoja.set_row(1, 40)
            hoja.set_row(3, 20)
            hoja.set_row(6, 30)
            hoja.set_row(7, 20)

            hoja.merge_range('B2:D2', 'REPORTE DE RUTA', merge_format_a)
            hoja.merge_range('E2:F2', 'Fecha Y Hora :', merge_format_d)
            hoja.merge_range('G2:I2', date.strftime('%d-%m-%Y  %H:%M:%S'), merge_format_c)

            hoja.merge_range('B4:D4', 'Nombre del Técnico', merge_format_d)
            hoja.merge_range('E4:G4', 'Usuario', merge_format_d)
            hoja.merge_range('H4:J4', 'Perido de tiempo', merge_format_d)
            hoja.merge_range('K4:M4','Distancia Recorrida (Km)', merge_format_d)
            hoja.merge_range('N4:P4','Tiempo Sin Actividad',merge_format_d)
            hoja.merge_range('Q4:R4','Tiempo de Ruta',merge_format_d)

            hoja.merge_range('B5:D5', f"{technician.name} {technician.last_name}",merge_format_b)
            hoja.merge_range('E5:G5', technician.user.email, merge_format_b)
            hoja.merge_range('H5:J5', day, merge_format_b)
            hoja.merge_range('K5:M5', data['distance_traveled'], merge_format_b)
            hoja.merge_range('N5:P5', data['idle_time'], merge_format_b)
            hoja.merge_range('Q5:R5', data['route_time'], merge_format_b)

            hoja.merge_range('B7:O7','HISTORIAL DE CAMBIOS',merge_format_e)
            hoja.merge_range('B8:C8', 'FECHA', merge_format_c)
            hoja.merge_range('D8:E8', 'HORA', merge_format_c)
            hoja.merge_range('F8:O8', 'CAMBIOS', merge_format_c)
            i = 9
            for data in changes:
                hoja.merge_range(f"B{i}:C{i}",data['date'], merge_format_b)
                hoja.merge_range(f"D{i}:E{i}", data['time'], merge_format_b)
                hoja.merge_range(f"F{i}:O{i}", data['change'], merge_format_b)
                i=i+1
            archivo.close()
            output.seek(0)
            filename = f"reporte_de_ruta_{day}_{technician}.xlsx"
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
            return response
        except Exception as e:
            raise e

def am_or_pm(data):

    if int(data) >= 0 and int(data) < 12:
        return 'am'
    elif int(data) >= 12 and int(data) < 24:
        return 'pm' 
    
def get_technical_and_availability(technician, day, operator):

    day_format = datetime.strptime(day, '%d-%m-%Y')

    if technician is None:
        schedule = Schedule.objects.filter( 
                                            schedule_start_date__lte=day_format,
                                            schedule_end_date__gte=day_format,
                                            technician__operator=operator
                                            ).select_related('technician')
    else:
        schedule = Schedule.objects.filter( 
                                            schedule_start_date__lte=day_format,
                                            schedule_end_date__gte=day_format,
                                            technician__operator=operator,
                                            technician = technician
                                            ).select_related('technician')
    
    number_day = datetime.strptime(day, '%d-%m-%Y').weekday() 
    list_data = []

    for data in schedule:

        disponibility = data.disponibility.values('ID', 'schedule_day')

        if len(disponibility) > 0 and disponibility is not None:

            for d in disponibility:

                dictionary = {'id_technician': data.technician.ID, 'id_disponibility': d['ID']}

                if (d['schedule_day'] == number_day ) and dictionary not in list_data:

                    list_data.append(dictionary)
    
    return list_data
            
def data_in_calendar_os(operator, month, week, year, day, technician, os_type):
    obj = calendar.Calendar()
    if week is not None and int(week) > 0 :
        obj_days = obj.monthdatescalendar(int(year), int(month))[int(week)-1]
    elif day is not None and week is None and int(day) > 0 and int(day) < 32:
        obj_days = [datetime.strptime(f"{day}-{month}-{year}",'%d-%m-%Y')]
    else:
        obj_days = obj.itermonthdates(int(year), int(month))

    os_in_calendar = []

    for day in obj_days:

        schedule = get_technical_and_availability(technician, day.strftime('%d-%m-%Y'), operator)

        if schedule is not None and len(schedule) > 0:

            for data in schedule:

                if os_type is None:
    
                    os_list = Os.objects.filter(
                                                technician=data['id_technician'], 
                                                technician__operator=operator,
                                                disponibility_hours__father=data['id_disponibility']
                                                )
                    
                else: 

                    os_list = Os.objects.filter(
                                                technician=data['id_technician'], 
                                                technician__operator=operator,
                                                disponibility_hours__father=data['id_disponibility'],
                                                ostype__ID = os_type
                                                )

                if len(os_list) > 0:
                    
                    for item_os in os_list:
                        os_in_calendar.append({
                                                'title': item_os.ostype.name,
                                                'start': f"{day.strftime('%d-%m-%Y')} {item_os.disponibility_hours.schedule_start_time.strftime('%H:%M')}",
                                                'end': f"{day.strftime('%d-%m-%Y')} {item_os.disponibility_hours.schedule_end_time.strftime('%H:%M')}",
                                                'color': item_os.ostype.color,
                                                'technician_id':item_os.technician.ID
                                            })          
                        
    if len(os_in_calendar) == 0:
        raise ValidationError({'message': 'No existen técnicos disponibles para esta fecha'})

    return Response({'data': os_in_calendar}, status=200)

class CalendarOsView(APIView):

    month_param = openapi.Parameter('month', openapi.IN_QUERY, 
    description="Fecha (mes) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    year_param = openapi.Parameter('year', openapi.IN_QUERY, 
    description="Fecha (año) final para hacer la busqueda",
    type=openapi.TYPE_STRING)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Id del operador a reagendar",
    type=openapi.TYPE_INTEGER)

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha (día) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    week_param = openapi.Parameter('week', openapi.IN_QUERY, 
    description="Número de semana para hacer la busqueda",
    type=openapi.TYPE_STRING)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Id del técnico a buscar",
    type=openapi.TYPE_INTEGER)

    os_type_param = openapi.Parameter('os_type', openapi.IN_QUERY, 
    description="Id del tipo de OS a buscar",
    type=openapi.TYPE_INTEGER)

    def get(self, request, *args, **kwargs):
        try:
            month = request.GET.get('month', None)
            year = request.GET.get('year', None)
            technician = request.GET.get('technician', None)
            week = request.GET.get('week',None)
            operator = request.GET.get('operator', None)
            day = request.GET.get('day', None)
            os_type = request.GET.get('os_type', None)

            if technician == '':
                technician = None
            if os_type == '': 
                os_type = None

            if month is not None and operator is not None and year is not None and week is None and day is None:
                calendar_list = data_in_calendar_os(operator, month, week, year, None, technician, os_type)
                return calendar_list
            elif month is not None and operator is not None and year is not None and week is not None and day is None:
                calendar_list = data_in_calendar_os(operator, month, week, year, None, technician, os_type)
                return calendar_list
            elif month is not None and operator is not None and year is not None and week is None and day is not None:
                calendar_list = data_in_calendar_os(operator, month, week, year, day, technician, os_type)
                return calendar_list
            else:
                raise ValidationError({'message': 'Parametros incompletos en Query'})
        except Exception as e:
            
            raise e


class RescheduleOSView(APIView):

    day_param = openapi.Parameter('day', openapi.IN_QUERY, 
    description="Fecha (día) para hacer la busqueda",
    type=openapi.TYPE_STRING)

    os_param = openapi.Parameter('os', openapi.IN_QUERY, 
    description="Id de la OS a reagendar",
    type=openapi.TYPE_INTEGER)

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Id del operador a reagendar",
    type=openapi.TYPE_INTEGER)

    technician_param = openapi.Parameter('technician', openapi.IN_QUERY, 
    description="Id del técnico a reagendar",
    type=openapi.TYPE_INTEGER)

    disponibility_hours_param = openapi.Parameter('hours', openapi.IN_QUERY, 
    description="Id de la disponibilidad a reagendar",
    type=openapi.TYPE_INTEGER)

    start_hours_param = openapi.Parameter('start', openapi.IN_QUERY, 
    description="Hora inicial a reagendar",
    type=openapi.TYPE_INTEGER)

    end_hours_param = openapi.Parameter('end', openapi.IN_QUERY, 
    description="Hora final a reagendar",
    type=openapi.TYPE_INTEGER)


    @swagger_auto_schema(manual_parameters=[day_param, operator_param, os_param])
    def get(self, request, *args, **kwargs):
        try:
            technician = request.GET.get('technician', None)
            now = datetime.now()
            operator_id = request.GET.get('operator', None)
            day = request.GET.get('day', None)
            os_id = request.GET.get('os', None)
            if os_id is not None and day is not None:
                os = Os.objects.filter(ID=int(os_id))
                if os[0].status == 7 and len(os) > 0:
                    time = Category.objects.get(ID=os[0].category.ID)
                    schedule_technician_response = list_of_technician_availables_method(operator_id, day,technician, 'disponibility')
                    seconds = int(time.duration) * 60
                    day_format=datetime.strptime(day, '%d-%m-%Y')
                    list_of_hour_range = []
                else: 
                    raise ValidationError({'message': 'Status actual de la OS no está En Reagendar'})

                if len(schedule_technician_response) == 0:

                    raise ValidationError({'message': 'Objeto no encontrado'})

                if day_format > now:

                    list_of_hour_range = list_of_hours_method(schedule_technician_response,seconds)

                    if len(list_of_hour_range) < 1:

                        raise ValidationError({'message':'Objeto no encontrado'})

                    return Response({'list_of_hour_range':list_of_hour_range},status=200)
                else: 
                    raise ValidationError({'message':'Fecha inválida'})

        except Exception as e:
            raise e
    
    @swagger_auto_schema(manual_parameters=[day_param, technician_param, operator_param, os_param, disponibility_hours_param, start_hours_param, end_hours_param])
    def post(self, request, *args, **kwargs):
        try:
            operator_id = request.GET.get('operator', None)
            day = request.GET.get('day', None)
            os_id = request.GET.get('os', None)
            technician_id = request.GET.get('technician', None)
            hours_id = request.GET.get('hours', None)
            start = request.GET.get('start', None)
            end = request.GET.get('end', None)
            os = Os.objects.filter(ID=int(os_id), operator=int(operator_id))
            if len(os) > 0:
                if (technician_id is not None and
                    hours_id is not None and
                    os_id is not None and
                    day is not None and
                    start is not None and 
                    end is not None) and os[0].status == 7:
                    father = Disponibility.objects.filter(ID=hours_id)
                    if len(father) > 0:
                        technician = Technician.objects.get(ID=technician_id)
                        direction = Direction.objects.get(id=father[0].dir.id)
                        child = Disponibility.objects.create(  
                                                        schedule_day = father[0].schedule_day,   
                                                        schedule_start_time=datetime.strptime(start,'%H:%M'),
                                                        schedule_end_time=datetime.strptime(end,'%H:%M'),
                                                        dir = direction,
                                                        schedule_status = 1,
                                                        father = father[0]
                                                        )
                        os[0].status = 0
                        os[0].technician = technician
                        os[0].disponibility_hours = child
                        os[0].save()
                        return Response({
                                            'data': {
                                                            'action':f"OS nro. {os[0].ID} reagendada al día {day} {child.schedule_start_time.strftime('%H:%M')} a {child.schedule_end_time.strftime('%H:%M')}",
                                                            'technician':f"ID: {os[0].technician.id_number} , 'name: {os[0].technician.name} {os[0].technician.last_name}", 
                                                            'os_type': f"{os[0].ostype.name}", 
                                                            'category': f"{os[0].category.name}"
                                                        }
                                            }, status=200)
                    else:
                        raise ValidationError({'message': "No se encontró una disponibilidad para reagendar OS"})
                else:
                    raise ValidationError({'message': "Campos requeridos para reagendar OS incompletos"})
            else:     
                raise ValidationError({'message': 'OS no encontrada'})
        except Exception as e:
            raise e
    


def get_user_information(operator,user_id):
    settings = OperatorSetting.objects.get(operator=operator)
    url= settings.config['operator_outside_sales_url']
    headers = {"Authorization":f"{settings.config['operator_authorization_token']}"}
    response = requests.get(url, headers=headers) 
    user = user_id
    if response.status_code == 200:#Sales oraculo get user ID
        if len(response.json()) > 0:#Response is not empty
            user = response.json()[0]['customer_user']
            if user :#User is not empty
                url = settings.config['operator_user_id_url'] + str(user)
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    if len(response.json()) > 0:
                        try:
                            user_full_name = response.json()['first_name'] + " " + response.json()['last_name']
                        except KeyError:
                            user_full_name = response.json()['name'] + " " + response.json()['last_name']
                        if len(user_full_name) < 1:
                            user_full_name = None
                        if response.json()['document_number']:
                            document_number = response.json()['document_number']
                        else: 
                            document_number = None 
                        context = {
                                    'name': user_full_name,
                                    'document_number': document_number           
                                } 
                        return context
        else: 
            url = settings.config['operator_user_id_url'] + str(user_id)
            response = requests.get(url, headers=headers)
            if response.status_code == 200:#Get user info from oraculo userapp api
                if len(response.json()) > 0:
                    user_full_name = response.json()['name'] + " " + response.json()['last_name']
                    if len(user_full_name) < 1:
                        user_full_name = None
                    if response.json()['document_number']:
                        document_number = response.json()['document_number']
                    else:
                        document_number = None 
                    context = {
                                    'name': user_full_name,
                                    'document_number': document_number           
                                } 
                    return context


class OsListingSearchEngineView(APIView):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Parámetro operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    generic_param = openapi.Parameter('generic', openapi.IN_QUERY, 
    description="Parámetro para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[operator_param, generic_param])
    def get(self, request, *args, **kwargs):
        try:
            operator = request.GET.get('operator', None)
            generic = request.GET.get('generic', None)
            list_of_os = []
            user = self.request.user
            if operator is not None and (generic is None):
                _qs =  Os.objects.filter(operator__ID=operator).filter(Q(technician__ID__in=user.technician.supervidados_ids)|
                                                                       Q(technician__ID=user.technician.ID))
                return Response(DetailOsSerializers( _qs, many=True).data, status=200)

            elif operator is not None and (generic is not None):
                try:
                    number = int(generic) 
                    q_objects = Q()
                    q_objects |= Q(ID=number)
                    q_objects |= Q(status=number)
                    q_objects |= Q(technician__ID=number)
                    q_objects |= Q(ostype__ID=number)
                    q_objects |= Q(category__ID=number)
                    q_objects |= Q(plan_id=number)
                    q_objects |= Q(user_id=number)
                    q_objects |= Q(sequential_id=number)
                    q_objects |= Q(plan_brujula__ID=number)
                    q_objects |= Q(user_brujula__document_number=number)
                    _qs = Os.objects.filter(operator__ID=operator).filter(Q(technician__ID__in=user.technician.supervidados_ids)|
                                                                          Q(technician__ID=user.technician.ID)).filter(q_objects)

                    return Response(DetailOsSerializers( _qs, many=True).data, status=200)

                except ValueError:
                    try:
                        day = datetime.strptime(generic,'%d-%m-%Y')
                        _qs = Os.objects.filter(operator__ID=operator).filter(Q(technician__ID__in=user.technician.supervidados_ids)|
                                                                              Q(technician__ID=user.technician.ID)).filter(created=day)
                        return Response(DetailOsSerializers( _qs, many=True).data, status=200)
                            
                    except ValueError:
                        phrase = str(generic)
                        q_objects = Q()
                        q_objects |= Q(ostype__name__icontains=phrase)
                        q_objects |= Q(category__name__icontains=phrase)
                        q_objects |= Q(technician__name__icontains=phrase)
                        q_objects |= Q(technician__last_name__icontains=phrase)
                        q_objects |= Q(operator__name__icontains=phrase)
                        q_objects |= Q(plan_brujula__tradename__icontains=phrase)
                        q_objects |= Q(user_brujula__first_name__icontains=phrase)
                        q_objects |= Q(user_brujula__last_name__icontains=phrase)
                        _qs = Os.objects.filter(operator__ID=operator).filter(Q(technician__ID__in=user.technician.supervidados_ids)|
                                                                              Q(technician__ID=user.technician.ID)).filter(q_objects)
                        return Response(DetailOsSerializers( _qs, many=True).data, status=200)
                        
            elif operator is None and generic is None:

                raise ValidationError({'message': 'No existe un operador para realizar la Búsqueda'}) 
            
            return Response(OsSerializers(list_of_os, many=True).data, status=200)
        
        except Exception as e:
            
            raise e

class GetTourSummary(APIView):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Parámetro operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    os_param = openapi.Parameter('os', openapi.IN_QUERY, 
    description="Parámetro id de la os para hacer la busqueda",
    type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[operator_param, os_param])
    def get(self, request, *args, **kwargs):
        try:
             
            os = Os.objects.get(ID=request.GET.get('os')) 
            id_operator = os.operator.ID

            if os is not None and id_operator is not None:
                displacement = Displacement.objects.filter( os__ID=os.ID, 
                                                            km_final__gt=0, os__operator__ID=id_operator, 
                                                            displacement_time__isnull=False).order_by('-date')
                if len(displacement) > 0:
                    data = {
                                'date': displacement[0].date, 
                                'direction_init': displacement[0].direction_init.name,
                                'direction_final': displacement[0].direction_final.name,
                                'km_init': displacement[0].km_init,
                                'km_init': displacement[0].km_final,
                                'displacement_time': displacement[0].displacement_time,
                                'estimated_time': displacement[0].displacement_time,
                                'medio_desplazamiento': medio_desplazamiento[displacement[0].medio_desplazamiento][1]
                            }
                    return Response(data, status=200)
                else: 
                    raise ValidationError({'message': 'No existe un desplazamiento finalizado para esta OS'})


        except Exception as e:
                raise e

class GetBrujulaPlanView(APIView):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Parámetro operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    def get(self, request, *args, **kwargs):
        o = self.request.query_params.get('operator')
        qs = OperatorPlans.objects.filter(operator=o)
        _search = self.request.query_params.get('tradename', None)
        if _search:
            qs = qs.filter(tradename__icontains=_search)
        return Response([{"tradename":plan.tradename, "technology":plan.technology} for plan in qs])


class GetOraculoPlanView(APIView):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Parámetro operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    def get_plans(self, settings, _operator):
        _search   = self.request.query_params.get('tradename', None) 
        _response = []
        
        try:
            url = settings.config['operator_oraculo_plans_url'].format(_operator)
            headers = {"Authorization":f"{settings.config.get('operator_oraculo_plans_token',' ')}"}
            peticion = requests.get(url, params={}, headers=headers)

            if peticion.status_code == 200:
                data_peticion = peticion.json()
            
                for plan in data_peticion:
                    if _search:
                        if _search.lower() in plan['tradename'].lower():
                            _response.append(plan)
                    else:
                        _response.append(plan)

                return _response
                
            else:
                return peticion.text
        
        except Exception as e:
            print (e)
            raise e

    def get_categories(self, settings):

        try:
            url = settings.config['operator_oraculo_kindplan_url']
            headers = {"Authorization":f"{settings.config.get('operator_oraculo_kindplan_token',' ')}"}
            peticion = requests.get(url, params={}, headers=headers)

            if peticion.status_code == 200:
                data_peticion = peticion.json()
                return data_peticion
                
            else:
                return peticion.text
        
        except Exception as e:
            raise e


    def get(self, request, *args, **kwargs):
        _operator = self.request.query_params.get('operator')
        settings = OperatorSetting.objects.get(operator=_operator)

        data = {
            "plans":self.get_plans(settings, _operator),
            "categories":self.get_categories(settings),            
        }
        return Response(data)