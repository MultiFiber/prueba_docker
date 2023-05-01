from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union

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

from .models import Ostype


class OstypeDatatable(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID", "created"]
    FIELDS_FILTERS: Dict[str, str] = {
        "ID": "int",
        "name":"str",
        "color":"str",
        "tag":"str",
    }

    model: BaseModel = Ostype

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
                    Q(name__icontains=search) |
                    Q(color__icontains=search)|
                    Q(sequential_id__icontains=search)|
                    Q(tag__icontains=search)
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """

        return {
            "ID": instance.ID,
            "name" : instance.name,
            "color" : instance.color,
            "tag": instance.tag,
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
            "name":"str",
            "color":"str",
            "tag":"str",
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
            "Nombre de la OS":{
                "field": "name",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Color":{
                "field": "color",
                "sortable": True,
                "visible": True,
                "position": 3,
                "width":100,
                "fixed":None
            },
            "Etiqueta":{
                "field": "tag",
                "sortable": True,
                "visible": True,
                "position": 4,
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

