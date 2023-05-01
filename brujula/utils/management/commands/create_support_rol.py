"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

GROUPS = ['developers', 'devops', 'qa', 'operators', 'product']
MODELS = ['Os', 'Technician']
PERMISSIONS = ['view', ]  # For now only view permission by default for all, others include add, delete, change

def create_support_rol():
    GROUPS = ['support']
    MODELS = ['Category', 'Direction', 'Operator', 'Operator_settings', 'Os', 'Disponibility', 'operator setting']
    PERMISSIONS = ['view', 'add', 'delete', 'change']
    for group in GROUPS:
            new_group, created = Group.objects.get_or_create(name=group)
            for model in MODELS:
                for permission in PERMISSIONS:
                    name = 'Can {} {}'.format(permission, model)
                    print("Creating {}".format(name))

                    try:
                        model_add_perm = Permission.objects.get(name=name)
                    except Permission.DoesNotExist:
                        logging.warning("Permission not found with name '{}'.".format(name))
                        continue

                    new_group.permissions.add(model_add_perm)


class Command(BaseCommand):
    help = 'Creates read only default permission groups for users'
    
    def handle(self, *args, **options):
        create_support_rol()
    print("Created default group and permissions.")



