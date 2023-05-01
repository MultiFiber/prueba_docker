from django.http import Http404
from django.utils.translation import gettext as _
from django.core.exceptions import PermissionDenied, BadRequest, ObjectDoesNotExist
from django.db import transaction
from django.conf import settings
from django.forms import ValidationError as FormValidationError
from rest_framework import exceptions
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from .permissions import DTPermissionDenied


def custom_exception_handler(exc, context):
    if hasattr(settings, 'raise_in_custom_exception'):
        raise exc
    
    if isinstance(exc, FormValidationError):

        if isinstance(exc, list):
            details = " \n".join(exc)
            data = {"message": details}
        else:
            data = {"message": str(exc)}
        return Response(data, status=400)

    if isinstance(exc, (exceptions.ValidationError,)):
        if isinstance(exc.detail, list):
            details = " \n".join(exc.detail)
            data = {"message": details}
        elif isinstance(exc.detail, dict):
            try:
                details = " ".join([txt for txt in exc.detail.values()])
                data = {"message": details}
            except TypeError  as e:
                details = " "
                for _e in exc.detail.items():
                    details = details + " ".join([txt for txt in _e[1]]) + " "
                    details = details.replace('Este campo',f'El campo {_e[0]}')
                data = {"message": details}

        else:
            data = {"message": exc.detail}

        if hasattr(exc,'detalle'):
            data['detail']=exc.detalle

        return Response(data, status=exc.status_code)

    elif isinstance(exc, (exceptions.ParseError, BadRequest )):
        msg = _('Error en peticion.')
        data = {'message': msg, 'detail':str(exc)}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        msg = _('Fallo en autenticacion.')
        detail = exc.detail
        data = {'message': msg  , 'detail': detail}
        return Response(data, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, PermissionDenied):
        msg = _('Usted no tiene permiso para realizar esta acción')
        data = {'message': msg }
        return Response(data, status=status.HTTP_403_FORBIDDEN)

    elif isinstance(exc, DTPermissionDenied):
        result = {"size": 0, "data": [], 'message':'Usted no puede vizualizar esta tabla'}
        return Response( result, status=status.HTTP_200_OK)

    elif isinstance(exc, (Http404 , ObjectDoesNotExist, exceptions.NotFound)):
        _obj = str(exc).split(' ')[0]
        msg = _(f'Objeto {_obj} no encontrado.')
        data = {'message': msg, 'detail':str(exc)}
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait
        if isinstance(exc.detail, (list, dict)):
            data = exc.detail
        else:
            data = {'message': exc.detail}
        return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR, headers=headers)

    return None
