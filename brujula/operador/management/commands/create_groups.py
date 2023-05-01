"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging
import copy
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.apps import apps

DEFAUL_MODELS = [
    'Os',
    'Disponibility',
    'OperatorSetting',
    'Category',
    'Direction',
    'Operator',
    'KeyValueOperator',
    'KeyValueSystem',
    'Client',
    'OperatorPlans',
    'OsPic',
    'Displacement',
    'TripSummary',
    'Ostype',
    'ReportRequest',
    'ReportDefinition',
    'HistorySession',
    'Technician',
    'TechnicianPic',
    'Schedule',
    'Disponibility',
    'Absence',
    'Holiday',
    'UserApp',
]


def base_permisos(GROUPS, MODELS, PERMISSIONS):
    for group in GROUPS:
        new_group, created = Group.objects.get_or_create(name=group)
        for model in MODELS:
            for permission in PERMISSIONS:
                codename = '{}_{}'.format(permission, model.lower())
                print("Creating {}".format(codename))

                try:
                    model_add_perm = Permission.objects.get(codename=codename)
                except Permission.DoesNotExist:
                    logging.warning("codename '{}' error.".format(codename))
                    # model_add_perm = Permission.objects.create(codename=codename)

                new_group.permissions.add(model_add_perm)



"""
Rol Administrador (Multifiber) y Soporte

    Orden de servicio

    Disponibilidad

    Estadísticas

    Configuración
"""
def create_admin_rol():
    GROUPS = ['admin']
    MODELS = [] + DEFAUL_MODELS
    PERMISSIONS = ['view', 'add', 'delete', 'change', 'datatable_view']
    base_permisos(GROUPS, MODELS, PERMISSIONS)



"""
Rol Multifiber (Solo Lectura, no puede ver los botones para crear, ni editar).

    Orden de servicio

    Disponibilidad

    Estadísticas

    Configuración
"""
def create_multifiber_rol():
    MODELS = [] + DEFAUL_MODELS
    PERMISSIONS = ['view', 'datatable_view']
    base_permisos(['multifiber'], MODELS, PERMISSIONS)



"""
Rol Administrador (ISP) (Solo ve la info de su ISP)

    Orden de servicio

    Disponibilidad

    Estadísticas

    Configuración

"""
def create_admin_isp_rol():
    GROUPS = ['admin_isp']
    MODELS = [] + DEFAUL_MODELS
    PERMISSIONS = ['view', 'datatable_view' ]
    base_permisos(GROUPS, MODELS, PERMISSIONS)



"""
Rol Supervisor  (ISP) (Solo ve la info de su ISP)

    Orden de servicio

    Disponibilidad

    Estadísticas

    Configuración (Solo sección de Tipos de OS)


"""
def create_supervisor_isp_rol():

    _excludes = ['UserApp','KeyValueOperator', 'KeyValueSystem','OperatorSetting']
    MODELS = [ x for x in DEFAUL_MODELS if x not in _excludes ]
    PERMISSIONS = ['view', 'datatable_view']
    base_permisos(['supervisor_isp'], MODELS, PERMISSIONS)


"""
Rol Servicio de Cliente  (ISP) (Solo ve la info de su ISP)

    Orden de servicio (Todo)

    Disponibilidad (Solo lectura)
"""

def create_client_service_isp_rol():
    GROUPS = ['client_service_isp']
    MODELS = [] + DEFAUL_MODELS
    PERMISSIONS = ['view', 'add', 'delete', 'change', 'datatable_view']
    base_permisos(GROUPS, MODELS, PERMISSIONS)



def create_perms():
    ContentType = apps.get_model("contenttypes", "ContentType")
    Permission = apps.get_model("auth", "Permission")

    excludes = ['django.contrib.admin',
                'django_filters',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',]

    ctypes = set()
    perms = []
    count_perms = []


    for app in django.apps.apps.get_app_configs():

        if app.name in excludes:
            continue

        if '.' in app.name:
            app.name = app.name.split('.').pop()

        app_config = apps.get_app_config(app.name)


        for klass in app_config.get_models():

            ctype = ContentType.objects.get_for_model(
                klass, for_concrete_model=False
            )
            ctypes.add(ctype)

            _m = klass._meta.object_name.lower()
            perms.append(
                Permission(codename=f'datatable_view_{_m}',
                           name='View Datatable',
                           content_type=ctype)
            )
            perms.append(
                Permission(codename=f'datatable_edit_columns_{_m}',
                           name='Edit Datatable columns',
                           content_type=ctype)
            )
            count_perms.append(f'datatable_view_{_m}')
            count_perms.append(f'datatable_edit_columns_{_m}')

        for _p in perms:
            print (f"Creando {_p}", end=' -> ')
            try:
                _p.save()
            except Exception as e:
                print (f'Ya existe {_p.codename}')
            else:
                print ('Creado ')
            
        #Permission.objects.bulk_create(perms)


class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'
    
    def handle(self, *args, **options):  
        #create_perms()

        create_multifiber_rol()
        create_supervisor_isp_rol()
        create_admin_rol()
        create_admin_isp_rol()
        create_client_service_isp_rol()

    print("Created default group and permissions.")