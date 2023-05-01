import re

from django.contrib.auth.hashers import check_password
from django.core.cache import cache

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import Permission
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token


from rest_framework_simplejwt import views as views_jwt
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from userapp.models import UserApp, ActionForUser
from sesionapp.models import HistorySession


def register_history_user(user, request, **kwargs):

    HistorySession.objects.create(
        user =user,
        ip = request.META['REMOTE_ADDR']
    )

def have_ec(word, email=False):
    if email == True:#Caso de que sea un email
        regexp = re.compile('[^0-9a-zA-Z]+@.')
        if regexp.search(word):
            return True
        else:
            return False
    else: 
        regexp = re.compile('[^0-9a-zA-Z]+')
        if regexp.search(word):
            return True
        else: 
            return False
        
class ObtainJWT(views_jwt.TokenViewBase):
    _serializer_class = api_settings.TOKEN_OBTAIN_SERIALIZER

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        
        # Buscar usuario y registrar        
        # register_history_user(request.user, request)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshJWT(views_jwt.TokenViewBase):
    _serializer_class = api_settings.TOKEN_REFRESH_SERIALIZER



class Auth(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def signin(self, request, version):
        try:
            email= request.data['email']
            password= request.data['password']
            user = UserApp.objects.get(email=email)

            if not user.is_active:
                raise ValidationError('Usuario no se encuentra activo o tiene problemas.')

            validate = check_password(password, user.password) 

            if validate:
                token, _ = Token.objects.get_or_create(user=user)
                register_history_user(user, request)
                data_cache = cache.get(f'user_perms_{user.ID}')
                if data_cache:
                    permission_list = data_cache
                    groups = cache.get(f'user_groups_{user.ID}')[0]

                else:
                    permissions_data_a = user.user_permissions.all()
                    permissions_data_b = ActionForUser.objects.filter(for_user__ID=user.ID)
                    permission_list = []

                    for data in permissions_data_a:
                        permission_list.append(data.codename)

                    for data in permissions_data_b:
                        permission_list.append(data.action.name)

                    all_group = user.groups.all()
                    if all_group.count() > 0:
                        groups = all_group.last().name
                        all_group_names = []
                        for _g in all_group:
                            all_group_names.append(_g.name)
                            for data in _g.permissions.all():
                                permission_list.append(data.codename)
                    else:
                        groups = ''
                        all_group_names = []

                    cache.set(f'user_perms_{user.ID}', list(set(permission_list)), 60*60)
                    cache.set(f'user_groups_{user.ID}', all_group_names , 60*60)


                return Response({'token': token.key,
                                'permissions': permission_list, 'rol':groups})

            else:
                raise ValidationError("Contraseña incorrecta")
        except UserApp.DoesNotExist:
            raise ValidationError("Correo no encontrado")
        except KeyError as err:
            exc = ValidationError('Debe proporcionar email y password')  
            exc.detalle = str(err)
            raise exc
    
    def signup(self, request, version):

        try:
            request.data['email']
            request.data['name']
            request.data['password']
        except KeyError as e:
            exc = ValidationError('Debe proporcionar email, password y name')  
            exc.detalle = str(err)
            raise exc

        exist = UserApp.objects.filter(email=request.data['email']).exists()
        if exist:
            exc = ValidationError('Ya existe un usuario con ese correo')  
            raise exc
        else:
            #*Caracteres especiales no permitidos
            if have_ec(request.data['name']):
                exc = ValidationError('No se permiten caracteres especiales en el campo name')  
                raise exc
            elif have_ec(request.data['last_name']):
                exc = ValidationError('No se permiten caracteres especiales en el campo last_name')  
                raise exc                
            elif have_ec(request.data['email'], True):
                exc = ValidationError('No se permiten caracteres especiales en el campo email')  
                raise exc                  
            else: 
                user = UserApp.objects.create(
                    name=request.data.get('name'),
                    last_name=request.data.get('last_name',''),
                    phone=request.data.get('phone',''),
                    password=request.data.get('password'),
                    email=request.data.get('email')
                )
                user.set_password(user.password)
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
                register_history_user(user, request)

                return Response({'error':False, 'token':token.key})

    def signout(self, request, version):
        token =  request.GET.get('token')
        token = Token.objects.filter(key=token).first()
        if token:
            token.delete()
            return Response({'mensaje': 'Sesion cerrrada exitosamente'},status=status.HTTP_200_OK)
        else:
            exc = ValidationError('Token no encontrado')  
            raise exc