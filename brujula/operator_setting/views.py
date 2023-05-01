from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action

from utils.views import BaseViewSet, BaseUpdateDetailsViewSet, get_user_by_token
from utils.helpers import cache

from .models import OperatorSetting
from .serializer import *

from django.utils.decorators import method_decorator

__all__ = ['OperatorSettingViewSetV1','OperatorSettingViewSetV2']


class OperatorSettingViewSetV1(BaseViewSet):
    serializer_class = OperatorSettingSerializer
    queryset = OperatorSetting.objects.all()
    filterset_fields = ( 'operator',)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return OperatorSetting.objects.all()
        return OperatorSetting.objects.filter(operator=self.request.user.operator)

    @action(detail=False, methods=['post'])
    def delete_key_cache(self, request) -> Response:
        if request.user.is_superuser:
            cache.delete()
            return Response()

class OperatorSettingViewSetV2(BaseUpdateDetailsViewSet):
    serializer_class = OperatorSettingSerializerV2
    filterset_fields = ( 'operator',)
    lookup_field = 'config'

    def get_queryset(self):
        user = self.request.user 
        
        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return OperatorSetting.objects.filter(operator__ID=o)
            return OperatorSetting.objects.all()

        return OperatorSetting.objects.filter(operator=user.operator)

    def get_object(self):
        _operator = self.kwargs['operador']
        _field = self.kwargs[self.lookup_field]
        _obj = OperatorSetting.objects.get(operator_id=_operator)

        if _field in _obj.config.keys():
            try:
                my_value = int(_obj.config[_field])
            except Exception as e:
                my_value = _obj.config[_field]
            return {
                self.lookup_field: my_value
            }
        else:

            if _field == 'operator_waiting_time_os_int':
                return {
                    self.lookup_field: 0
                }                

            raise NotFound('No se encuentra esta config')

    def update(self, request, *args, **kwargs):   
        user  =  get_user_by_token(request);
        request.data['updater'] = user.ID

        instance = self.get_object()
        _operator = self.kwargs['operador']
        _field = self.kwargs[self.lookup_field]
        _obj = OperatorSetting.objects.get(operator_id=_operator)

        if instance:
            _obj.config[_field] = request.data.get('valor')
            _obj.save()
        else:

            _obj.config = {
                **_obj.config,
                _field: request.data.get('valor')
            }
            _obj.save()

        return Response(request.data)
