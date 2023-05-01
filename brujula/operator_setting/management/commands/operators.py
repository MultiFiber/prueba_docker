"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

from operator_setting.models import * 


class Command(BaseCommand):
    help = 'Comando para administrar al operador'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('parameters', nargs='+', type=str)


    def _config(self, *args, **kwargs):
        p = kwargs['parameters']
        if p[1] == 'show_config':
            _settings = OperatorSetting.objects.all()

            if p[2] == 'all':

                for _ in _settings:
                    print (_.config)
                
                return True


            for _ in _settings:
                try:
                    c = _.config[p[2]]
                    print (f'Operator: {_.operator.name} valor {c}.')
                except Exception as e:
                    print (f'Operator: {_.operator.name} no tiene {p[1]}.')

        if p[1] == 'update_config':

            _settings=OperatorSetting.objects.all()
            for _ in _settings:
                try:
                    _.config[p[2]] = p[3]
                    _.save()
                    print (f'Operator: {_.operator.name} actualizado.')
                except Exception as e:
                    print (f'Operator: {_.operator.name} no tiene {p[2]}.')


    def _counts(self, *args, **kwargs):
        print (args)

    def handle(self, *args, **kwargs):
        p = kwargs['parameters']

        if 'config' in p[0]:
            self._config(*args, **kwargs)

        if 'count' in p[0]:
            self._counts(*args, **kwargs)