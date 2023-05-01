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
from userapp.models import *


def verde_ok(ok):
    print(Style.BRIGHT + "[ " + Fore.GREEN + ok + Fore.RESET + " ]" + Style.RESET_ALL) 


def verde_1(ok):
    print(Style.BRIGHT + "[ " + Fore.GREEN + ok, end=': ') 

def verde_2(ok):
    print(Fore.RESET + " ]" + Style.RESET_ALL) 

class Command(BaseCommand):
    help = 'Comando para administrar al operador'

    def add_arguments(self, parser):
        # Positional arguments
        #parser.add_argument('parameters', nargs='+', type=str)
        ...


    def handle(self, *args, **kwargs):
        #p = kwargs['parameters']
        sys.stdout.flush()
        
        with open('DATA.JSON', 'w', encoding="utf-8") as file_data:

            verde_1('UserApp')

            file_data.write( serializers.serialize("jsonl", UserApp.objects.filter() ) )
            verde_2()

            file_data.write( serializers.serialize("jsonl", Operator.objects.filter() ) )
            verde_ok('Operator')

            file_data.write( serializers.serialize("jsonl", OperatorSetting.objects.filter() ) )
            verde_ok('OperatorSetting')

            file_data.write( serializers.serialize("jsonl", Technician.objects.filter() ) )
            verde_ok('Technician')
            
            file_data.write( serializers.serialize("jsonl", Ostype.objects.filter() ) )
            verde_ok('Ostype') 

            file_data.write( serializers.serialize("jsonl", Category.objects.filter() ) )
            verde_ok('Category')
            
            file_data.write( serializers.serialize("jsonl", Direction.objects.filter() ) )
            verde_ok('Direction')  
            
            file_data.write( serializers.serialize("jsonl", Disponibility.objects.filter() ) )
            verde_ok('Disponibility')  
            
            file_data.write( serializers.serialize("jsonl", OperatorPlans.objects.filter() ) )
            verde_ok('OperatorPlans')  

            file_data.write( serializers.serialize("jsonl", Client.objects.filter() ) )
            verde_ok('Technician')  



