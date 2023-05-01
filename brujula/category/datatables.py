from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union

import pytz
import requests
from utils.datatables import BaseDatatables
from utils.models import BaseModel
#from utils.utilitarian import get_token, matrix_url
from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet
from userapp.models import UserApp
from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from dynamic_preferences.registries import global_preferences_registry

from .models import Category


class CategoryDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "created":"datetime",
        "name":"str",
        "sequential_id": "int",
        "duration":"str",
        "img":"str",
        "questions":"str",
        "os_type":"Str",
        "description":"str",
    }

    model: BaseModel = Category

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
                    Q(name__icontains=search) |
                    Q(duration__icontains=search) |
                    Q(imgs__icontains=search) |
                    Q(questions__icontains=search) |
                    Q(os_type__icontains=search) | 
                    Q(sequential_id__icontains=search) | 
                    Q(description__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """
        #print(instance.imgs['value'])
        user = Category.history.filter(ID=instance.ID)
        if len(user) > 0:
            name_user = UserApp.objects.filter(ID=user[0].creator_id)
            if len(name_user) > 0:
                name_user = name_user[0].email
            else:
                name_user = None
        else:
            name_user = None
        return {
            "ID": instance.ID,
            "sequential_id": instance.sequential_id,
            "created": instance.created,
            "name" : instance.name,
            "duration" : instance.duration,
            "imgs" : instance.imgs,
            "questions": instance.questions,
            "os_type": instance.os_type.ID,
            "description": instance.description,
            "user": name_user
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
            "name": "str",
            "imgs": "list",
            "questions": "list",
            "technician": "list",
            "name_os_type": "list",
            "duration": "str",
            "user": "str",
            "description": "str"
        }

        data_struct["columns"] = {
            "Nombre":{
                "field": "name",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Duración":{
                "field": "duration",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Imágenes a solicitar":{
                "field": "imgs",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Preguntas":{
                "field": "questions",
                "sortable": True,
                "visible": True,
                "position": 4,
                "width":100,
                "fixed":'right'
            },
            "Usuario":{
                "field": "user",
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

