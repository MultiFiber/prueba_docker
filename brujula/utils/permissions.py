from django.contrib.auth.models import Permission

from rest_framework import permissions
from rest_framework.permissions import DjangoModelPermissions as BaseDjangoModelPermissions


class OnlyView(permissions.BasePermission):

    def has_permission(self, request, view):
        print ('')
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        print ('')
        return super().has_object_permission(request, view, obj)


class DTPermissionDenied(Exception):
    pass

class DjangoModelPermissions(BaseDjangoModelPermissions):
    pass

class DTDjangoModelPermissions(DjangoModelPermissions):
    
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.datatable_view_%(model_name)s'],
        'PUT': ['%(app_label)s.datatable_edit_columns_%(model_name)s'],
        'PATCH': ['%(app_label)s.datatable_edit_columns_%(model_name)s'],
        'DELETE': ['%(app_label)s.datatable_delete_columns_%(model_name)s'],
    }

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        _perms = [perm % kwargs for perm in self.perms_map[method]]
        #print (_perms)
        return _perms


    def has_permission(self, request, view):
        res = super().has_permission(request, view)
        all_perm = request.user.user_permissions.all() | Permission.objects.filter(group__user=request.user)
        # for _p in all_perm:
        #     print (_p.codename)
        print (request.user.has_perm('datatable_view_category'))
        if not res:
            raise DTPermissionDenied
        return True