import requests
import os

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union

from operator_setting.models import OperatorSetting
from utils.datatables import BaseDatatables
from utils.models import BaseModel
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import Os, Displacement


class OsDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, datetime] = {
        "ID": "int",
        "created" : "datetime",
        "client" : "str",
        "Doc. de identidad": "int",
        "technician" : "str",
        "status" : "str",
        "ostype":'int'
    }

    model: BaseModel = Os

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
                    
                    Q(created__icontains=search) | 
                    Q(status__icontains=search) |
                    Q(technician__name__icontains=search) |
                    Q(technician__last_name__icontains=search) |
                    Q(ostype__name__icontains=search) |
                    Q(category__name__icontains=search)|
                    Q(technology__icontains=search) |
                    Q(operator__name__icontains=search) |
                    Q(plan_id__icontains=search) |
                    Q(user_id__icontains=search)|
                    Q(direction__name__icontains=search)|
                    Q(plan_brujula__tradename__icontains=search)|
                    Q(user_brujula__first_name__icontains=search)|
                    Q(user_brujula__last_name__icontains=search)


                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        user_full = ''
        user = ''
        document_number = ''

        if instance.user_brujula == '' or instance.user_brujula is None:
            try:
                settings = OperatorSetting.objects.get(operator=instance.technician.operator)
                headers = {"Authorization":f"{settings.config['operator_authorization_token']}"}
                user_id = instance.user_id
                new_url = settings.config['operator_user_id_url'] + str(user_id)
                response = requests.get(new_url, headers=headers)
                if response.status_code == 200:
                    if len(response.json()) > 0:
                        try:
                            user = response.json()['first_name'] + " " + response.json()['last_name']
                        except KeyError:
                            user = response.json()['name'] + " " + response.json()['last_name']
                        user_full = response.json()
                        if response.json()['document_number']:
                            document_number = response.json()['document_number']
                        else: 
                            document_number = None

                else:#Reintento 1
                    url = settings.config['operator_user_id_url'] + str(user_id)
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:#Get user info from oraculo userapp api
                        if len(response.json()) > 0:
                            try:
                                user = response.json()['first_name'] + " " + response.json()['last_name']
                            except KeyError:
                                user = response.json()['name'] + " " + response.json()['last_name']
                            user_full = response.json()
                            if response.json()['document_number']:
                                document_number = response.json()['document_number']
                            else:
                                document_number = None

                    
            except Exception as e:

                user = '-'
                user_full = {}
                document_number = '-'
        else:
            _client = instance.user_brujula
            user_full = {
                "first_name": _client.first_name,
                "last_name": _client.last_name,
                "document_type": _client.document_type,
                "document_number":  _client.document_number,
                "email": _client.email,
                "phone": _client.phone           
            }
            user = user_full['first_name']
            document_number = user_full['document_number']


        def get_date():
            if instance.disponibility_hours.date is not None:
                return instance.disponibility_hours.date.strftime('%d-%m-%Y')
            else:
                return None


        return {
            "id_unico": instance.ID,
            "ID":instance.sequential_id,
            "fecha" : get_date(),
            "user" : user,
            "user_full":user_full,
            "document_number": document_number,
            "ostype" : instance.ostype.name,
            "technician" : instance.technician.name,
            "status" : str(instance.get_status_display()),
            "category_imgs":instance.category.imgs,
            "category_questions":instance.category.questions
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
        "Fecha" : "datetime",
        "Cliente" : "str",
        "Doc. de identidad": "int",
        "Tipo" : "str",
        "Tecnico" : "str",
        "Status" : "str"
        }

        data_struct["columns"] = {
            "ID":{
                "field": "ID",
                "sortable": True,
                "visible": True,
                "position": 10,
                "width":100,
                "fixed":'right'
            },        
            "Fecha":{
                "field": "fecha",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Cliente":{
                "field": "user",
                "sortable": True,
                "visible": True,
                "position": 9,
                "width":100,
                "fixed":'right'
            },
            "Doc de Identidad":
            {
                "field": "document_number",
                "sortable": True,
                "visible": True,
                "position": 11,
                "width":100,
                "fixed":'right'
            },
            "Tipo":{
                "field": "ostype",
                "sortable": True,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":None
            },
            "Técnico":{
                "field": "technician",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Status":{
                "field": "status",
                "sortable": True,
                "visible": True,
                "position": 2,
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
            "Tipo de orden":{
               "type":"int",
               "name":"ostype",
            }

        }

        return data_struct


class DisplacementDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "created":"datetime",
        "direction_init":"str",
        "direction_final":"str",
        "medio_desplazamiento":"str",
        "displacement_time":"str",
        "km_final":"str",
        "os":"str"
    }

    model: BaseModel = Displacement

    def get_initial_queryset(self) -> QuerySet:
        qs: BaseModel = self.model.objects.all().exclude(deleted=True)
        operator: str = self.request.data.get('operator', '')
        operator_str = str(operator)

        if operator_str.isnumeric() == True and operator != '0':
            qs: BaseModel = qs.filter( os__operator=int( operator ) )

        return qs

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        search: str = self.SEARCH

        if search:

            if search.isdigit():

                qs: QuerySet = qs.filter( ID=int(search) )
            
            else:
                
                qs: QuerySet = qs.filter( 
                    Q(created__icontains=search) | 
                    Q(date__icontains=search) |
                    Q(direction_init__icontains=search) |
                    Q(direction_final__icontains=search) |
                    Q(km_init__icontains=search) |
                    Q(km_final__icontains=search) |
                    Q(os__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:
        return {
            "ID": instance.ID,
            "created": instance.created.strftime('%d-%m-%Y'),
            "direction_init": instance.direction_init.name,
            "direction_final": instance.direction_final.name,
            "km_init": instance.km_init,
            "km_final": instance.km_final,
            "os": instance.os.sequential_id,
            "medio_desplazamiento": instance.get_medio_desplazamiento_display(),
            "displacement_time": instance.displacement_time
        }


    def get_struct(self) -> Dict[str, Any]:
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
            "created": "datetime",
            "direction_init":"str",
            "direction_final":"str",
            "medio_desplazamiento":"str",
            "displacement_time":"str",
            "km_final":"str"
        }

        data_struct["columns"] = {
            "Fecha":{
                "field": "created",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Origen":{
                "field": "direction_init",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Destino":{
                "field": "direction_final",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Medio":{
                "field": "medio_desplazamiento",
                "sortable": True,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":'right',
            },
            "Tiempo":{
                "field": "displacement_time",
                "sortable": True,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":'right'
            },
            "Recorrido":{
                "field": "km_final",
                "sortable": True,
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

        }
        return data_struct
