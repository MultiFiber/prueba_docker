import ast
import calendar
import os
import requests
from datetime import datetime
from typing import Any, Callable, Dict, List, Union

#from .utilitarian import communications_url, get_token

from utils.models import BaseModel
from django.db.models.query import QuerySet
from django.http import JsonResponse
from django_datatables_view.base_datatable_view import BaseDatatableView
from rest_framework.serializers import ValidationError
from utils.helpers import cache

import random


class BaseDatatables(BaseDatatableView):

    """

        Class return Datatables of Models Class
    
    """

    def __init__(self, request):

        self.request = request

    
    FIELDS_EXCEL: Dict[str, Dict[str, str]] = {}
    FIELDS_FILTERS: Dict[str, str] = {}
    FIELDS_SORTABLE: List[str] = []

    TYPE_OF_FILTERS: Dict[str, List[str]] = {
        "datetime": [ "equal", "year", "month", "day", "week_day", "week", "quarter", "gt", "gte", "lt", "lte", "different" ],
        "str": [ "equal", "iexact", "icontains", "istartswith", "iendswith", "different" ],
        "int": [ "equal", "gt", "gte", "lt", "lte", "different" ],
        "bool": [ "equal", "different" ],
        "choices": [ "equal", "different" ],
        "location": [ "equal", "different"],
    }

    COMPARISON: Dict[str, List[str]] = {
        "equal": ["datetime", "str", "int", "bool", "choices"],
        "year": ["int"],
        "month": ["int"],
        "day": ["int"],
        "week_day": ["int"],
        "week": ["int"],
        "quarter": ["int"],
        "gt": ["datetime", "str", "int", "bool"],
        "gte": ["datetime", "str", "int", "bool"],
        "lt": ["datetime", "str", "int", "bool"],
        "lte": ["datetime", "str", "int", "bool"],
        "different": ["datetime", "str", "int", "bool"],
        "iexact": ["str"],
        "icontains": ["str"],
        "istartswith": ["str"],
        "iendswith": ["str"]
    }

    def get_filtered_search(self, qs: QuerySet) -> QuerySet:

        """

            This function, search queryset

            :returns: Filtered querySet with search field

        """

        return qs

    def get_struct(self) -> Dict[str, Any]:
        
        """

            This function, get datables struct

            :returns: Dict, with datatables definitions

        """

        return {
            "id_table": None,
            "fields":{},
            "columns":{},
            "filters":{},
            "comparisons": {
                "Igual": {
                    "name": "equal",
                    "type": ["datetime", "str", "int", "bool", "choices", "location"]
                },
                "Año": {
                    "name": "year",
                    "type": ["int"]
                },
                "Mes": {
                    "name": "month",
                    "type": ["int"]
                },
                "Día": {
                    "name": "day",
                    "type": ["int"]
                },
                "Día de la semana": {
                    "name": "week_day",
                    "type": ["int"]
                },
                "Semana": {
                    "name": "week",
                    "type": ["int"]
                },
                "Trimestre": {
                    "name": "quarter",
                    "type": ["int"]
                },
                "Mayor": {
                    "name": "gt",
                    "type": ["datetime", "str", "int", "bool"]
                },
                "Mayor o igual": {
                    "name": "gte",
                    "type": ["datetime", "str", "int", "bool"]
                },
                "Menor": {
                    "name": "lt",
                    "type": ["datetime", "str", "int", "bool"]
                },
                "Menor o igual": {
                    "name": "lte",
                    "type":"datetime"
                },
                "Distinto": {
                    "name": "different",
                    "type": ["datetime", "str", "int", "bool", "choices", "location"]
                },
                "Similar": {
                    "name": "iexact",
                    "type":"str"
                },
                "Contiene": {
                    "name": "icontains",
                    "type":"str"
                },
                "Inicia con": {
                    "name": "istartswith",
                    "type":"str"
                },
                "Termina con": {
                    "name": "iendswith",
                    "type":"str"
                }
            },
            "type_of_comparisons":{
                "datetime": [ "Igual", "Año", "Mes", "Día", "Día de la semana", "Semana", "Trimestre", "Mayor", "Mayor o igual", "Menor", "Menor o igual", "Distinto"  ],
                "str": [ "Igual", "Similar", "Contiene", "Inicia con", "Termina con", "Distinto"],
                "int": [ "Igual", "Mayor", "Mayor o igual", "Menor", "Menor o igual", "Distinto" ],
                "bool": [ "Igual", "Distinto" ],
                "choices": [ "Igual", "Distinto" ],
                "location": [ "Igual", "Distinto" ]
            }
        }

    def get_initial_params(self):

        """

            This function, set initial params

        """

        def scheme_filter(self, _filter: List[str]) -> List[str]:

            """
            
                This funtion, return validate filter or raise exception with errors

            """

            def type_validation(_type: str, value: str, name: str, comparison_filter: str) -> Any:

                """
            
                    This funtion, return validated filter value or raise exception with errors

                """

                def validate_datetime(value: str, _type: str, comparison_filter: str) -> Union[datetime, int]:

                    """
            
                        This funtion, return validated datetime value or raise exception with errors

                    """

                    if comparison_filter in ["year", "month", "day", "week_day", "week", "quarter"]:

                        result: int = int(value)

                        if comparison_filter == "year" and 2100 >= result <= 2000:

                            raise ValidationError({})

                        elif comparison_filter == "month" and 1 >= result <= 12:

                            raise ValidationError({})

                        elif comparison_filter == "day":

                            max_days: int = 366 if calendar( datetime.now().year ) else 365

                            if not 1 >= result <= max_days:

                                raise ValidationError({})

                        elif comparison_filter == "week_day" and 0 >= result <= 6:

                            raise ValidationError({})

                        elif comparison_filter == "quarter" and 1 >= result <= 4:

                            raise ValidationError({})

                    else:

                        result: str = datetime.strptime(value, '%d/%m/%Y %H:%M')

                    return result

                def validate_bool(value: str, _type: str, comparison_filter: str) -> bool:

                    """
                    
                        This function, return validated bool value or raise exception with errors
                    
                    """

                    if not value in ["True", "False"]:

                        raise Exception("Invalid bool value")

                    else:

                        return True if value == "True" else False

                def validate_int(value: str, _type: str, comparison_filter: str) -> int:

                    """
                    
                        This function, return validated int value or raise exception with errors
                    
                    """

                    return int(value)

                def validate_str(value: str, _type: str, comparison_filter: str) -> str:

                    """
                    
                        This function, return validated str value or raise exception with errors
                    
                    """

                    return str(value)

                def validate_choices(value: str, _type: str, comparison_filter: str) -> int:

                    """
                    
                        This function, return validated int value or raise exception with errors
                    
                    """

                    return int(value)

                def validate_location(value: str, _type: str, comparison_filter: str) -> str:

                    """
                    
                        This function, return validated lcoation value or raise exception with errors
                    
                    """

                    result: List[str] = value.split(':')

                    if not ( len(result) == 2  and result[0] in ['region','commune','street','streetLocation'] and result[1].isdigit() ):

                        raise Exception("Invalid location value")

                    return value

                dict_validators: Dict[str, Callable] = {
                    "int":validate_int,
                    "str":validate_str,
                    "datetime":validate_datetime,
                    "bool":validate_bool,
                    "choices":validate_choices,
                    "location":validate_location,
                }
                
                try:

                    value: Any = dict_validators[_type](value, _type, comparison_filter)

                except Exception as e:

                    raise ValidationError({
                        "Invalid value type": f"Invalid value: {value}, for filter {name}",
                    })

                return value

            if len(_filter) == 3:

                name_filter: str = _filter[0]
                comparison_filter: str = _filter[1]
                value_filter: str = _filter[2]

                #Get filter name or None
                field_type: str = self.FIELDS_FILTERS.get(name_filter)

                if field_type:

                    #Get filter comparison or None
                    comparisons: List[str] = self.TYPE_OF_FILTERS[field_type]

                    if comparison_filter in comparisons:
 
                        value_filter: Any = type_validation(field_type, value_filter, name_filter, comparison_filter)

                    else:

                        raise ValidationError({
                            "Invalid filter comparison": f"Invalid comparison name {comparison_filter}",
                        })

                else:

                    raise ValidationError({
                        "Invalid filter name": f"Invalid filter name {name_filter}",
                    })

            else:

                raise ValidationError({
                    "Invalid filter": "Invalid filter length",
                })

            return [name_filter, comparison_filter, value_filter]

        #Filters list
        filters: List[List[str]] = self.request.data.get('filters', "[]")
        validated_filters: List[list] = []

        try:

            #Get filters list
            filters: List[list] = ast.literal_eval(filters)
            
        except Exception as e:

            raise ValidationError({
                "Invalid filter": "Invalid filter struct",
            }) 

        if isinstance(filters, list) :

            for _filter in filters:

                #Filter validation
                validated_filters.append(scheme_filter(self, _filter))

        else:

            raise ValidationError({
                "Invalid filter": "Invalid filter struct",
            })   

        #Save validated filters
        self.REQUEST_FILTERS: List[List[str]] = validated_filters
        
        #Save Slice
        self.START: int = int( self.request.data.get('start', 0) )
        self.OFFSET: int = int( self.request.data.get('offset', 10) )

        #Save column order
        self.COLUMN_ORDER_FIELD: str = self.request.data.get('order_field', 'ID')

        if not self.COLUMN_ORDER_FIELD in self.FIELDS_SORTABLE:

            raise ValidationError({
                "Invalid sortable column": f"Invalid sortable column called {self.COLUMN_ORDER_FIELD}",
            })

        self.COLUMN_ORDER_TYPE: str = self.request.data.get('order_type', 'desc')
        
        if not self.COLUMN_ORDER_TYPE in ["desc", "asc"]:

            raise ValidationError({
                "Invalid sortable column type": f"Invalid sortable column type called {self.COLUMN_ORDER_TYPE}",
            })

        #Save search value
        self.SEARCH: str = self.request.data.get('search', '')

    def get_initial_queryset(self) -> QuerySet:
        
        """

            This function, filter queryset by operator

        """

        #Base QuerySet
        qs: BaseModel = self.model.objects.all().exclude(deleted=True)

        #Select instances of QuerySet of indicates operator
        operator: str = self.request.data.get('operator', '')
        operator_str = str(operator)

        if operator_str.isnumeric() == True and operator != '0':

            #Exclude by Operator
            qs: BaseModel = qs.filter( operator=int( operator ) )

        else:

            ValidationError({
                "Error operator": "Don't send operator or invalid value",
            })

        return qs

    def get_filtered_queryset(self) -> QuerySet:

        """

            This function, filter queryset by filters

        """

        qs: QuerySet = self.get_initial_queryset()
        filters_dict: Dict[str, Any] = {}
        excludes_dict: Dict[str, Any] = {}
        
        for _fitler in self.REQUEST_FILTERS:

            filter_name: str = _fitler[0]
            fitler_comparison: str = _fitler[1]
            value: Any = _fitler[2]

            if  isinstance(value, str) and self.FIELDS_FILTERS[filter_name] == "datetime" \
                and not fitler_comparison in ["year", "month", "day", "week_day", "week", "quarter"]:

                value = datetime.strptime(value, '%d/%m/%Y %H:%M')

            if fitler_comparison == "equal":

                filters_dict[filter_name] = value

            elif fitler_comparison == "different":

                excludes_dict[filter_name] = value

            else:

                filters_dict[f"{filter_name}__{fitler_comparison}"] = value

        if filters_dict:

            qs: QuerySet = qs.filter(**filters_dict)

        if excludes_dict:

            qs: QuerySet = qs.exclude(**excludes_dict)

        return qs

    def get_ordered_queryset(self, qs: QuerySet) -> QuerySet:

        """

            This function, order queryset

        """

        if self.COLUMN_ORDER_FIELD and self.COLUMN_ORDER_TYPE:

            column_order: str = self.COLUMN_ORDER_FIELD

            if self.COLUMN_ORDER_TYPE == "desc":

                column_order: str = f"-{column_order}"

            qs: QuerySet = qs.order_by(column_order)

        return qs

    def get_instance_to_dict(self, instance: BaseModel) -> Dict[str, Any]:

        """

            This function, return dict of instance

        """

        return instance.__dict__

    def get_data(self) -> JsonResponse:

        """

            This function, return dict of instance

        """
        
        self.get_initial_params()

        key_cache = "{}_{}_{}_{}_{}_{}_{}_{}".format(
        self.START, self.OFFSET, self.COLUMN_ORDER_FIELD,
        self.FIELDS_SORTABLE, self.COLUMN_ORDER_TYPE,
        self.SEARCH, self.request.data.get('filters', "[]"),
        self.request.build_absolute_uri()
        )
        data_cache = cache.get(key_cache)
        #print (key_cache)
        if data_cache:
            return JsonResponse( data_cache, safe=False)

        
        result: List[Dict[str, Any]] = []

        qs: QuerySet = self.get_ordered_queryset( self.get_filtered_search( self.get_filtered_queryset() ) )
        qs_size = qs.count()

        if qs:
        
            qs: QuerySet = qs[self.START: self.START + self.OFFSET]
            
            result: List[Dict[str, Any]] = list( map(lambda instance: self.get_instance_to_dict(instance), qs) )

        #print (key_cache)
        result = {"size":qs_size, "data": result}
        cache.set(key_cache, result, 60*60)
        return JsonResponse( result, safe=False)

    def get_qs_to_data(self, qs: QuerySet) -> List[Dict[str, Any]]:

        """

            This function, process data

        """

        return []

    def download_data(self) -> QuerySet:

        """

            This function, return file of data

        """

        self.get_initial_params()
        
        result: List[Dict[str, Any]] = self.get_qs_to_data( 
            self.get_ordered_queryset( 
                self.get_filtered_search( 
                    self.get_filtered_queryset() 
                ) 
            ) 
        )

        #Define excel
        wb = Workbook()
        ws1 = wb.active
        redFill = PatternFill(
                    start_color='3bd464',
                    end_color='3bd464',
                    fill_type='solid',
                )

        for key, value in self.FIELDS_EXCEL.items():

            ws1[f'{key}1'].fill: PatternFill = redFill
            ws1[f'{key}1']: str = value

        #Create rows
        for row in result:
            if 'Recontactos' in self.FIELDS_EXCEL.values():
                recontactos = row[11]
                row[11] = " "
                communications = row[12]
                row[12] = " "
            ws1.append(row)
            if 'Recontactos' in self.FIELDS_EXCEL.values():
                for recontacto in recontactos:
                    ws1.append(recontacto)
                for communication in communications:
                    ws1.append(communication)

        #Save file
        _random: int = random.randint(5000, 5000000)
        path: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path_file: str = f'{path}/media/files/{_random}.xlsx'
        wb.save(filename=path_file)

        #Send file
        with open(path_file, 'rb') as file_excel:

            sesion = requests.Session()
            sesion.headers.update({"Authorization": get_token()})
            sesion.post(
                url=communications_url('email-list'),
                data={
                    'message': 'Reporte de datos',
                    'subject': 'Reporte',
                    'receiver': self.request.data['email'],
                    'sender': 'reporte@Iris.cl',
                    'operator': int(self.request.data['operator'])
                },
                files={
                    'reporte.xlsx':file_excel,
                },
                verify=False,
            )

    class Meta:
        
        abstract: bool = True

