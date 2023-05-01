import django_filters.rest_framework

from datetime import datetime
from typing import Any, Dict, List, Union

from django.contrib.auth.models import User
from django.db.models import Model
from django.http import JsonResponse
from django.conf import settings

from rest_framework import generics, mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from utils.permissions import OnlyView, DjangoModelPermissions, DTDjangoModelPermissions
from utils.models import BaseModel
from utils.pagination import VerySmallResultsSetPagination
from utils.helpers import cache
from userapp.models import UserApp


def get_user_by_token(request):
    if not request.user:
        user_id = Token.objects.get(key=request.auth).user_id
        user = UserApp.objects.get(pk=user_id)
        return user  
    else:
        return request.user


class BaseViewSet(viewsets.ModelViewSet):

    """

        Class define base of all viewset.
    
    """

    filter_fields: Union[list, str]  = '__all__'
    history_ignore_fields: List[str] = []
    filter_backends: List[Any] = [django_filters.rest_framework.DjangoFilterBackend,OrderingFilter]
    ordering_fields: Union[list, str] = '__all__'
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    #pagination_class = VerySmallResultsSetPagination

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return [OnlyView()]
        elif 'datatable' in str(self.action):
            return [DTDjangoModelPermissions()]
        return super().get_permissions()


    def get_extra_serializer(self, request, data):
        try:
            data['creator'] = request.user.ID
            data['updater'] = request.user.ID
            return data
        except Exception as e:
            return {
                **data,
                **{'creator':request.user.ID, 'updater':request.user.ID}
            }
        
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_object(self, *args, **kwargs):
        if hasattr(self, 'name_key_object'):
            name_key = self.name_key_object
        else:
            name_key = self.serializer_class.__name__.\
            replace("Serializers","").replace("Serializer","")

        key_cache = 'get_object_v1_{}_{}'.format(name_key,self.kwargs.get('pk'))
        data_cache = cache.get(key_cache)
        if data_cache:
            return data_cache

        obj = super().get_object(*args, **kwargs)
        cache.set(key_cache, obj, settings.CACHES_TIMES['max'])
        return obj

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        user  =  get_user_by_token(request);
        request.user = user
        data = self.get_extra_serializer(request, request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    def custom_list_response(self, request, *args, **kwargs):
        return []

    def list(self, request, *args, **kwargs):
        user  =  get_user_by_token(request);
        request.user = user
        full_url = request.build_absolute_uri()
        if False:
            return custom_list_response(request, *args, **kwargs)


        key_cache = 'list_{}_{}'.format(full_url, user.pk)
        data_cache = cache.get(key_cache)

        if data_cache:
           return Response(data_cache)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            print (len(page), queryset.count())
            serializer = self.get_serializer(page, many=True)
            cache.set(key_cache, serializer.data, 60*60)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        cache.set(key_cache, serializer.data, 60*60)
        return Response(serializer.data)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user  =  get_user_by_token(request);
        #request.data['updater'] = user.ID
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    

    @action(detail=True, methods=['get'])
    def history(self, request, pk: int = None) -> JsonResponse:

        """
            
            This function returns Historical changes of instance model
            :param self: Instance of ViewSet
            :type self: ViewSet Class extend of BaseViewSet
            :returns: List of str, this contains fields of Model defined in Viewset
            :rtype: list
        
        """
 
        def get_fields(self: BaseViewSet) -> List[str]:

            """
            
                This function returns fields of defined Model in Viewset
                :param self: Instance of ViewSet
                :type self: ViewSet Class extend of BaseViewSet
                :returns: List of str, this contains fields of Model defined in Viewset
                :rtype: list
            
            """

            return [ field.name for field in type(self.queryset[0])._meta.fields]

        def get_first(self: BaseViewSet, instance ) -> Dict[str, Any]:

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
            the_txt_field = f"{change_aux.updater} modifico el campo {change.field} de {the_old_field} a {the_new_field}",
            return the_txt_field


        #Get instance of model to get history
        try:
            
            instance_model: BaseModel = self.queryset.get(ID=pk)
            
            #Cache
            #key_cache = 'history_v1_{}_{}'.format(instance_model._meta.object_name, pk)
            #data_cache = cache.get(key_cache)
            #if data_cache:
            #    print ('si esta en la cache')
            #    return JsonResponse( data_cache, safe=True)
            #
            #End cache

            #Get history of instance
            instance_model_history: BaseModel = instance_model.history.all()

            if len(instance_model_history) == 0:
                result: Dict[str, Any] = {
                    'first': {},
                    'changes': [],
                }
                return JsonResponse(result, safe=True)

            #Get first value of instance
            first: Dict[str, Any] = get_first(self, instance_model_history[len(instance_model_history) - 1])

            #Cache management

            # data_history = []
            # for item in instance_model_history:
            #     print (item.history_id)
            #     m = item.instance_type._meta.object_name
            #     key_cache = 'history_{}_{}'.format(m, item.ID)
            #     history_cache = cache.get(key_cache) 
            #     print (history_cache)
            #     if not history_cache:
            #         cache.set(key_cache, item, 60)

            #End cache

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

            
            # new_changes = []
            # for c in result['changes']:

            #     if c["updater"]["old_value"] != int and c["updater"]["old_value"] != float:
            #         c["updater"]["old_value"] = str(c["updater"]["old_value"])
            #         c["updater"]["new_value"] = str(c["updater"]["new_value"])
                
                
            #     if c.get("logo") != None:
            #         new_changes.append({"logo": {"old_value":c['logo']['old_value'].name,  "new_value":c['logo']['new_value'].name}})
            #     else:
            #         new_changes.append(c)

                
            # result['changes'] = new_changes
            #cache.set(key_cache, result, 60 * 60 * 24)
            return JsonResponse( result, safe=True)
        except ObjectDoesNotExist:
            return JsonResponse({"error":True,"mensaje":"dato no existente"})


class MultipleChoicesMixins():
    choices_response = {}

    def get_choices_response(self):
        return self.choices_response

    def reformat_object(self, array):
        return [{"id": obj[0], "ID": obj[0], "name": obj[1]} for obj in array]


class MultipleChoicesAPIView(MultipleChoicesMixins, APIView):
    def get(self, request, **kwargs):
        return Response({key: self.reformat_object(value) for key, value in self.get_choices_response().items()})


class MultipleChoicesViewSet(MultipleChoicesMixins, viewsets.ModelViewSet):
    
    @action(detail=False, methods=['get'])
    def form(self, request, version, **kwargs):
        return Response({key: self.reformat_object(value) for key, value in self.get_choices_response().items()})        


                   
                   
class BaseUpdateDetailsViewSet(mixins.RetrieveModelMixin,
                               mixins.UpdateModelMixin,
                               viewsets.GenericViewSet):

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user  =  get_user_by_token(request);
        request.data['updater'] = user.ID
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print('EDITADO')
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)