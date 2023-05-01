from os import name
import random
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Union

import pytz
import requests
from utils.dataTables import BaseDatatables
from utils.models import BaseModel
#from common.utilitarian import get_token, matrix_url
from dateutil.relativedelta import relativedelta
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
#from dynamic_preferences.registries import global_preferences_registry

from .models import HistorySession


class SesionDatatables(BaseDatatables):

    FIELDS_SORTABLE: List[str] = ["ID","user", "date", "ip"]
    FIELDS_FILTERS: Dict[str, str] = {
        "user":"str",
        "date":"datetime",
        "ip":"str",
    }

    model: BaseModel = HistorySession

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
                    Q(user__icontains=search) | 
                    Q(date__icontains=search) |
                    Q(ip__icontains=search) 
                ).distinct()


        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """

        return {
            "user": instance.user.name,
            "date": instance.date,
            "ip": instance.ip,
        }

    def get_struct(self) -> Dict[str, Any]:

        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        data_struct: Dict[str, Any] = super().get_struct()

        data_struct["defaults"] = {
            "order_field":"user",
            "order_type":"desc",
            "start":0,
            "offset":10,
            "filters":[],
            "search":"",
            "scroll":800,
        }

        data_struct["fields"] = {
            "user":"str",
            "date":"datetime",
            "ip":"str",
        }

        data_struct["columns"] = {
            "Actividad":{
                "field": "user",
                "sortable": True,
                "visible": True,
                "position": 1,
                "width":100,
                "fixed":None
            },
            "Fecha":{
                "field": "date",
                "sortable": True,
                "visible": True,
                "position": 2,
                "width":100,
                "fixed":None
            },
            "Ip":{
                "field": "ip",
                "sortable": False,
                "visible": True,
                "position": 3,
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
            "Fecha de fin":{
                "type":"datetime",
                "name":"created",
                "format":"%d/%m/%Y %H:%M",
            },
            "user":{
                "type":"str",
                "name":"user"
            },

        }

        return data_struct


