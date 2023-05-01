import requests

from django.http import JsonResponse
from django.contrib.auth.models import Group

from rest_framework import viewsets
from OS.models import Os

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from utils.permissions import OnlyView, DjangoModelPermissions
from utils.views import BaseViewSet, MultipleChoicesAPIView
from .models import UserApp, status_user
from operator_setting.models import OperatorSetting
from .serializer import UserAppSerializer
from .datatables import UserDatatables


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserappFormChoicesList(MultipleChoicesAPIView):
    """
    List all choices for status, medio_desplazamiento
    """
    choices_response = {"status_user": status_user}


class MiProfileView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        headers = ''
        for header, value in request.META.items():
            if not header.startswith('HTTP'):
                continue
            header = '-'.join([h.capitalize() for h in header[5:].lower().split('_')])
            headers += '{}: {}\n'.format(header, value)
        print (headers)
        
        _token = print (request.headers.keys() )
        user_id = Token.objects.get(key=request.auth).user_id
        user = UserApp.objects.get(pk=user_id)      
        serializer = UserAppSerializer(user)
        return Response(serializer.data)


class UserAppViewSet(BaseViewSet):
    serializer_class = UserAppSerializer   
    queryset = UserApp.objects.all()
    filterset_fields = ('ID','name', 'last_name', 'email', 'phone', 'is_staff')

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return UserApp.objects.filter(operator__ID=o)
            return UserApp.objects.all()

        return UserApp.objects.filter(operator=user.operator)
    
    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(UserDatatables(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return UserDatatables(request).get_data()



class ListUsers(viewsets.ViewSet):

    operator_param = openapi.Parameter('operator', openapi.IN_QUERY, 
    description="Id del operador a buscar usuarios en Oráculo",
    type=openapi.TYPE_INTEGER)

    @swagger_auto_schema(manual_parameters=[operator_param])
    def get_oraculo_user(self,request):
        operator = request.GET.get('operator', None)
        try:
            if operator is not None:
                settings = OperatorSetting.objects.get(operator__ID=operator)
                token_oraculo = settings.config['operator_all_users_authorization_token']  
                url_oraculo = settings.config['operator_all_users_url']  
                lista_ids = Os.objects.filter(user_id__isnull=False).distinct('user_id')
                headers = {"Authorization": token_oraculo}
                response_clientes = []
                for cliente in lista_ids:
                    peticion = requests.get(url_oraculo+str(cliente.user_id), headers=headers)
                    if peticion.status_code == 200:
                        peticion = peticion.json()
                        response_clientes.append({'ID': peticion["ID"], 'mombre':peticion['name'],'apellido': peticion['last_name'], 'email': peticion['email'], 'telefono': peticion['phone']})
                    else:
                        response_clientes.append({'error':True})
            return JsonResponse(response_clientes, safe=False)
        except:
            return JsonResponse({'error': True,'mensaje': "error ocurrido"}, status=404)


    def get_all_users(self, request):
        try:
            _operator = self.request.query_params.get('operator')
            _tipo_busqueda = self.request.query_params.get('tipo_busqueda')
            _valor_busqueda = self.request.query_params.get('valor_busqueda')
            settings = OperatorSetting.objects.get(operator=_operator)
            
            data = {
                "evento": "Busqueda_usuarios",
                "tipo_busqueda":_tipo_busqueda,
                "valor_busqueda":_valor_busqueda,
            }
        
            url = settings.config['operator_all_users_url']
            headers = {"Authorization":f"{settings.config.get('operator_all_users_authorization_token',' ')}"}
            peticion = requests.post(url, json=data, headers=headers)
            response_clients = []
            print(peticion.text)

            if peticion.status_code == 200:
                data_peticion = peticion.json()
            
                for client in data_peticion:
                    response_clients.append(client)
                return JsonResponse({'success': True, 'users': response_clients})
            else:
                return JsonResponse({'success': False, 'mensaje': peticion.text})
        
        except Exception as e:
            return JsonResponse({'error': True, 'mensaje' : str(e)})


class ListGroups(viewsets.ViewSet):

    def get_groups(self,request):
        try:
            groups = Group.objects.only("id","name")
            qs = []
            for group in groups:
                qs.append({"name":group.name, "ID": group.id})
            return JsonResponse(qs, safe=False)
        except Exception as e:
            return JsonResponse({'error': True, 'mensaje' : str(e)})

