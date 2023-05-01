"""
Create permission groups
Create permissions (read only) to models for a set of groups
"""
import logging, sys

from django.core.management.base import BaseCommand
from django.core import serializers


from colorama import Fore
from colorama import Style
from colorama import init

from operator_setting.models import * 
from operador.models import * 
from tecnico.models import *
from category.models import *
from ostype.models import *
from OS.models import *
from direction.models import *



def verde_ok(ok):
    print(Style.BRIGHT + "[ " + Fore.GREEN + ok + Fore.RESET + " ]" + Style.RESET_ALL) 


class Command(BaseCommand):
    help = 'Comando para administrar al operador'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('parameters', nargs='+', type=str)
        ...

    def handle(self, *args, **kwargs):
        sys.stdout.flush()
        filename = kwargs['parameters'][0]

        with open(filename, encoding="utf-8") as file_data:
            print("Leyendo el archivo")
            data = file_data.read()

        modelos = []

        for obj in serializers.deserialize("jsonl", data):
            try:
                verde_ok(str(obj))
                obj.save()
            except Exception as e:
                print("E:",e)
                pass        