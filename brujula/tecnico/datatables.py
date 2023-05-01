from ast import operator
from contextlib import redirect_stderr
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union
from urllib import response
from userapp.models import UserApp
import pytz
import requests
from utils.datatables import BaseDatatables
from utils.models import BaseModel
#from utils.utilitarian import get_token, matrix_url
from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from dynamic_preferences.registries import global_preferences_registry
from operador.models import Operator

from .models import Disponibility, Holiday, Schedule, Technician, Absence


class ScheduleDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "created":"datetime",
        "schedule_start_date":"str",
        "schedule_end_date":"str",
        "technician":"str",
        "disponibility":"str",
        "absence":"str",
    }

    model: BaseModel = Schedule

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter(ID=int(search))
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(technician__ID__icontains=search)|
                    Q(created__icontains=search) | 
                    Q(schedule_start_date__icontains=search) |
                    Q(schedule_end_date__icontains=search) |
                    Q(technician__user__email__icontains=search) |
                    Q(disponibility__ID__icontains=search) |
                    Q(absence__ID__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """
        def get_absence_list(self, param : List[str]):
            response = list()
            for item in param:
                response.append((item[0], Operator.objects.filter(ID=item[1]).values_list('name', flat=True)[0]))
            return response
        
        def get_duration():
            if instance.schedule_start_date is not None and instance.schedule_end_date is not None:
                days = (datetime.strptime(instance.schedule_start_date.strftime('%d-%m-%Y'), '%d-%m-%Y') - datetime.strptime(instance.schedule_end_date.strftime('%d-%m-%Y'), '%d-%m-%Y')).days
                days = f"{days*(-1)+1} días"
            elif instance.schedule_start_date is not None and instance.schedule_end_date is None:
                days = "En curso"
            return days

        return {
            "ID": instance.ID,
            "period" : f"{instance.schedule_start_date.strftime('%d/%m/%Y')} - {instance.schedule_end_date.strftime('%d/%m/%Y')}",
            "email" : instance.technician.user.email if instance.technician.user else '',
            "duration" : get_duration(),
            "location": [dispo for dispo in instance.disponibility.values_list('dir__name', flat=True)]
        }


    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"ID",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] = {
            "ID": "int",
            "period": "datetime",
            "email": "str",
            "location": "list",
            "duration": "str"
        }

        data_struct["columns"] = {
            "ID":{
                "field": "ID",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Período":{
                "field": "period",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Duración":{
                "field": "duration",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":'right'
            },
            "Localizacion":{
                "field": "location",
                "sortable": True,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":None
            },
            "Técnico":{
                "field": "email",
                "sortable": True,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":None
            },

        }

        data_struct["filters"] = {

            "Fecha de inicio":{
                "type":"datetime",
                "name":"created",
                "format":"%d/%m/%Y %H:%M",
            },
            #"Fecha de fin":{
            #    "type":"datetime",
            #    "name":"created",
            #    "format":"%d/%m/%Y %H:%M",
            #},
#            "Rut":{
#                "type":"str",
#                "name":"rut"
            #},

        }

        return data_struct


class AbsenceDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "ID": "int",
        "Nombre del Técnico":"str",
        "Fecha de inicio": "datetime",
        "Correo electronico": "str",
        "Status": "str",
        }

    model: BaseModel = Absence

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter( ID=int(search) )
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(created__icontains=search) | 
                    Q(status__icontains=search) |
                    Q(operator__icontains=search) |
                    Q(technician__icontains=search) |
                    Q(id_type__icontains=search) |
                    Q(user__icontains=search) |
                    Q(start_time__icontains=search) |
                    Q(sequental_id__icontains=search) |
                    Q(end_time__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """
        def get_name(type, number):
            schedule_status = [
                (0, 'Disponible'),
                (1, 'No disponible'),
                (2, 'En almuerzo'),
                (3, 'Ausente'),
                ]
            absence_status = (
                (0, 'Pendiente'),
                (1, 'Aprovada'),
                (2, 'Rechazada'),
            )
            schedule_days = [
                (0, 'Lunes'),
                (1, 'Martes'),
                (2, 'Miercoles'),
                (3, 'Jueves'),
                (4, 'Viernes'),    
                (5, 'Sabado'),
                (6, 'Domingo'),
                ]
            documentos = [
                (0, 'pasaporte'),
                (1, 'dni')
                ]
            if type == "day":
                for data in schedule_days:
                    if data[0] == number:
                        return data[1]
            elif type == "status": 
                for data in absence_status:
                    if data[0] == number:
                        return data[1]
            elif type == "document":
                for data in documentos:
                    if data[0] == number:
                        return data[1]

        def get_technician(type,id):
            technician = Technician.objects.filter(operator=id).values('name', 'last_name','id_type','user')
            for data in technician:
                user_name = UserApp.objects.get(ID=data['user'])
                if type == "name":
                    return data['name'] + " " + data['last_name']
                elif type == "id_type":
                    return get_name("document", data['id_type'])
                elif type == "user":
                    return user_name.email
    
        return {
            "ID": instance.ID,
            "name": get_technician("name",instance.operator.ID), #name
            "start_time": instance.start_time,
            "email": get_technician("user",instance.operator.ID),    #email
            "status" : get_name("status",instance.status), #status
        }


    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"ID",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] = {
            "ID": "int",
            "Nombre del Técnico": "str",
            "Fecha de inicio": "datetime",
            "Correo electronico": "str",
            "Status": "str",
        }

        data_struct["columns"] = {
            "ID":{
                "field": "ID",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Nombre del Técnico":{
                "field": "name",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Fecha de inicio":{
                "field": "start_time",
                "sortable": True,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":'right'
            },
            "Correo electronico":{
                "field": "email",
                "sortable": True,
                "visible": True,
                "position": 8,
                "width":100,
                "fixed":None
            },
            "Status":{
                "field": "status",
                "sortable": True,
                "visible": True,
                "position": 6,
                "width":100,
                "fixed":None
            }
        }

        data_struct["filters"] = {

            "Fecha de inicio":{
                "type":"datetime",
                "name":"created",
                "format":"%d/%m/%Y %H:%M",
            },
            #"Fecha de fin":{
            #    "type":"datetime",
            #    "name":"created",
            #    "format":"%d/%m/%Y %H:%M",
            #},
#            "Rut":{
#                "type":"str",
#                "name":"rut"
            #},

        }

        return data_struct


class DisponibilityDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "created":"datetime",
        "schedule_status":"str",
        "schedule_day":"str",
        "dir":"str",
        "schedule_start_time":"datetime",
        "schedule_end_time":"datetime"
    }

    model: BaseModel = Disponibility

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter( ID=int(search) )
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(created__icontains=search) | 
                    Q(schedule_status__icontains=search) |
                    Q(schedule_day__icontains=search) |
                    Q(dir__icontains=search) |
                    Q(schedule_start_time__icontains=search) |
                    Q(schedule_end_time__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """
        return {
            "ID": instance.ID,
            "created": instance.created,
            "schedule_status" : instance.get_schedule_status_display(),
            "schedule_day" : instance.get_schedule_day_display(),
            "dir" : instance.dir.name,
            "schedule_start_time": instance.schedule_start_time,
            "schedule_end_time": instance.schedule_end_time
        }


    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"ID",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] = {
            "ID": "int",
            "created": "datetime",
            "schedule_status": "str",
            "schedule_day": "str",
            "dir": "str",
            "schedule_start_time": "datetime",
            "schedule_end_time" : "datetime"
        }

        data_struct["columns"] = {
            "Fecha de creación":{
                "field": "created",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Estado de Horario":{
                "field": "schedule_status",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Estado de Día":{
                "field": "schedule_day",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Dirección":{
                "field": "dir",
                "sortable": True,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":None
            },
            "Hora de Inicio Programada":{
                "field": "schedule_start_time",
                "sortable": True,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":'right'
            },
            "Hora de Finalización Programada":{
                "field": "schedule_end_time",
                "sortable": False,
                "visible": True,
                "position": 6,
                "width":100,
                "fixed":'right'
            },
        }

        data_struct["filters"] = {

            "Fecha de inicio":{
                "type":"datetime",
                "name":"created",
                "format":"%d/%m/%Y %H:%M",
            },
            #"Fecha de fin":{
            #    "type":"datetime",
            #    "name":"created",
            #    "format":"%d/%m/%Y %H:%M",
            #},
#            "Rut":{
#                "type":"str",
#                "name":"rut"
            #},

        }

        return data_struct


class TechnicianDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "ID":"int",
        "Nombre completo":"str",
        "Telefono":"str",
        "Correo electronico": "str",
        "Rol": "str",
        "status":"str",
    }

    model: BaseModel = Technician

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter( ID=int(search) )
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(status__icontains=search) |
                    Q(user__icontains=search) |
                    Q(password__icontains=search)|
                    Q(phone__icontains=search)
                ).distinct()

        return qs

    def get_extra(self, instance):
        my_supervisees = instance.supervidados_obj.values('ID','name','last_name')

        return {
        "my_supervisees":list(my_supervisees),
        "my_supervisor":list(instance.supervised_by.values('ID','name','last_name')),
            "technician":{
                'ID':instance.ID,
                'name':instance.name,
                'last_name':instance.last_name,
                'birthday':instance.birthday,
                'status':instance.status,
                'id_number':instance.id_number,
                'id_type':instance.id_type,
                'phone':instance.user.phone if (instance.user and instance.user.phone) else '',
            }
        }

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:        
        def get_role(supervisor):
            if supervisor == True:
                return 'Supervisor'
            else:
                return 'Técnico'


        return {
            "ID": instance.ID,
            "name": instance.full_name,
            "phone": instance.user.phone if (instance.user and instance.user.phone) else '',
            "user": instance.user.email if (instance.user and instance.user.email) else '',
            "role": get_role(instance.is_supervisor),
            "status": instance.get_status_display(),
            **self.get_extra(instance)
        }

    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"ID",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] ={
            "ID":"int",
            "Nombre completo":"str",
            "Telefono":"str",
            "Correo electronico": "str",
            "Rol": "str",
            "status":"str",
        }

        data_struct["columns"] = {
            "ID":{
                "field": "ID",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Nombre Completo":{
                "field": "name",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":'right'
            },
            "Teléfono":{
                "field": "phone",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":'right'
            },
            "Correo electronico":{
                "field": "user",
                "sortable": False,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":'right'
            },
            "Rol":{
                "field": "role",
                "sortable": False,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":'right'
            },
            "Status":{
                "field": "status",
                "sortable": False,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":'right'
            }
            
        }

        data_struct["filters"] = {
            "ID":{
                "type":"int",
                "name":"ID",
            },
            "Nombre Completo":{
                "type":"str",
                "name":"name",
            },
            "Usuario":{
                "type":"str",
                "name":"user",
            },
        }

        return data_struct


class HolidayDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "created":"datetime",
        "day":"datetime",
        "name":"str",
        "status":"str",
        "holiday_type":"str",
        "sequential_id": "int",
        "Operator": "str"
    }

    model: BaseModel = Holiday

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter( ID=int(search) )
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(created__icontains=search) | 
                    Q(day__icontains=search) |
                    Q(name__icontains=search) |
                    Q(status__icontains=search) |
                    Q(operator__name__icontains=search) |
                    Q(holiday_type__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """
        def get_name(type, number):
            schedule_status = [
                (0, 'Disponible'),
                (1, 'No disponible'),
                (2, 'En almuerzo'),
                (3, 'Ausente'),
                ]
            schedule_days = [
                (0, 'Lunes'),
                (1, 'Martes'),
                (2, 'Miercoles'),
                (3, 'Jueves'),
                (4, 'Viernes'),    
                (5, 'Sabado'),
                (6, 'Domingo'),
                ]

            if type == "day":
                for data in schedule_days:
                    if data[0] == number:
                        return data[1]
            elif type == "status": 
                for data in schedule_status:
                    if data[0] == number:
                        return data[1]
            
        return {
            "ID": instance.ID,
            "sequential_id": instance.sequential_id,
            "created": instance.created,
            "day":get_name('day',instance.day),
            "name":instance.name,
            "status":get_name('status',instance.status),
            "holiday_type":instance.holiday_type,
            "operator": instance.Operator.name,
            "operator_id": instance.Operator.ID,
        }


    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"ID",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] = {
            "ID": "int",
            "created": "datetime",
            "day":"datetime",
            "name":"str",
            "status":"str",
            "holiday_type":"str",
            "operator": "str"
        }

        data_struct["columns"] = {
            "Fecha de creación":{
                "field": "created",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Día de festividad":{
                "field": "day",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Nombre de la festividad":{
                "field": "name",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Estado":{
                "field": "status",
                "sortable": True,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":None
            },
            "Tipo de festividad":{
                "field": "holiday_type",
                "sortable": True,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":'right'
            },
            "Operador":{
                "field": "operator",
                "sortable": True,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":'right'
            },
        }

        data_struct["filters"] = {

            "Fecha de inicio":{
                "type":"datetime",
                "name":"created",
                "format":"%d/%m/%Y %H:%M",
            },
            #"Fecha de fin":{
            #    "type":"datetime",
            #    "name":"created",
            #    "format":"%d/%m/%Y %H:%M",
            #},
#            "Rut":{
#                "type":"str",
#                "name":"rut"
            #},

        }

        return data_struct


class TechnicianCategoriesDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "categories":"str",
        "technician": "int"
    }

    model: BaseModel = Technician

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter( ID=int(search) )
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(categories__name__icontains=search) |
                    Q(categories__os_type__name__icontains=search)
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """
        os_type = {}
        list_data = []
        data = [cat for cat in instance.categories.values('os_type__ID', 'name', 'os_type__name')]
        for d in data:

            if d['os_type__name'] in os_type:
                if [d['name']] not in os_type[d['os_type__name']]:
                    os_type[d['os_type__name']][1].append(d['name'])
                
            else: 
                os_type[d['os_type__name']] = [d['os_type__ID'], [d['name']]]

        for key, value in os_type.items():
            list_data.append({ 
                                'ID': value[0],
                                'os_type_name': key,
                                'categories_name':value[1]
                             })
        return list_data


    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"ID",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] = {
            "ID": "int",
            "os_type_name": "int",
            "categories_name": "list",
        }

        data_struct["columns"] = {
            "Tipo de orden de servicio":{
                "field": "os_type",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Categorias":{
                "field": "categories",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            }
        }

        data_struct["filters"] = {

            "Fecha de inicio":{
                "type":"datetime",
                "name":"created",
                "format":"%d/%m/%Y %H:%M",
            },
            #"Fecha de fin":{
            #    "type":"datetime",
            #    "name":"created",
            #    "format":"%d/%m/%Y %H:%M",
            #},
#            "Rut":{
#                "type":"str",
#                "name":"rut"
            #},

        }

        return data_struct