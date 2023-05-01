from os import name
import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union

import pytz
import requests
from utils.datatables import BaseDatatables
from utils.models import BaseModel
#from common.utilitarian import get_token, matrix_url
from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
#from dynamic_preferences.registries import global_preferences_registry

from .models import UserApp


class UserDatatables(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "name", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "ID":"int",
        "name": "str",
        "email": "str",
        "phone":"str",
        "status":"str",
    }

    model: BaseModel = UserApp

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
                    Q(email__icontains=search) |
                    Q(USERNAME_FILED__icontains=search) |
                    Q(sequential_id__icontains=search) |
                    Q(is_active__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:
        if self.request.user.groups.filter(name__in=['supervisor_isp']):
            #Supervisor comercial no debe ver esta tabla
            return {}

        return {
            "ID": instance.ID,
            "name": f"{instance.name} {instance.last_name}" ,
            "phone": instance.phone,
            "email": instance.email,
            "status": 'Activo' if instance.is_active else 'Inactivo',
        }

    def get_struct(self) -> Dict[str, Any]:
        if self.request.user.groups.filter(name__in=['supervisor_isp']):
            #Supervisor comercial no debe ver esta tabla
            return {}

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
            "ID":"int",
            "Nombre completo": "str",
            "Teléfono":"str",
            "Correo electrónico": "str",
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
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Teléfono":{
                "field": "phone",
                "sortable": False,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":None
            },
            "Correo electronico":{
                "field": "email",
                "sortable": False,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":None
            },
            "Status":{
                "field": "status",
                "sortable": False,
                "visible": True,
                "position": 5,
                "width":100,
                "fixed":None
            },
        }

        data_struct["filters"] = {
            "ID":{
                "type":"int",
                "name":"name"
            },
            "Nombre Completo":{
                "type":"str",
                "name":"name"
            },
            "Status":{
                "type":"str",
                "name":"status"
            },

        }

        return data_struct


