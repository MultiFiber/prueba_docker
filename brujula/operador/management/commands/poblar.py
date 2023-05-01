import logging
import random
from django_seed import Seed
from django.core.management.base import BaseCommand
from django.db import transaction
from operador.models import * 
from ostype.models import * 
from tecnico.models import * 
from userapp.models import * 
from category.models import * 
from direction.models import * 
from OS.models import *

logging.getLogger('faker').setLevel(logging.ERROR)

class Command(BaseCommand):

    def counter(self, my_list, my_counter):
        pass

    def handle(self, **options):

        seeder = Seed.seeder(locale='es_CL')
        #seeder = Seed.seeder()

        with transaction.atomic():

            seeder.add_entity(Direction, 100)
            seeder.add_entity(UserApp, 100)
            seeder.add_entity(Operator, 15)
            seeder.add_entity(Ostype, 100)
            seeder.execute()

            list_ostype = [item for item in Ostype.objects.all()]
            contador = 20 - len(list_ostype) if len(list_ostype) > 20 else 20
            seeder.add_entity(Category, 20 , {
                'os_type':lambda x: random.choice(list_ostype),
            })

            list_operador = [item for item in Operator.objects.all()]
            list_user = [item for item in UserApp.objects.all()]

            seeder.add_entity(Technician, 100, {
                'operator':lambda x: random.choice(list_operador),
                'user_id': lambda x: random.choice(list_user),
            })
            list_dir = [item for item in Direction.objects.all()]
            seeder.add_entity(Disponibility, 100,{
                'dir': lambda x: random.choice(list_dir),
            })

            seeder.add_entity(Absence, 100, {
                'operator':lambda x: random.choice(list_operador),
                })

            seeder.execute()
            return 'True'

            list_technician = [item for item in Technician.objects.filter(status=0)]
            list_disponibility = [item for item in Disponibility.objects.all()]
            seeder.add_entity(Schedule, 100, {
                'technician':   lambda x: random.choice(list_technician),
                'disponibility':lambda x: random.choice(list_disponibility),
            })

            list_category = [item for item in Category.objects.all()]
            seeder.add_entity(Os, 100, {
                'technician':   lambda x: random.choice(list_technician),
                'ostype':       lambda x: random.choice(list_ostype),
                'category':     lambda x: random.choice(list_category),
                'operator':     lambda x: random.choice(list_operador),
                'disponibility':lambda x: random.choice(list_disponibility),
            })

            seeder.execute() 

            list_os = [item for item in Os.objects.all()]

            seeder.add_entity(Displacement, 100, {
                'os':lambda x: random.choice(list_os),
                'direction_init':lambda x: random.choice(list_dir),
                'direction_final':lambda x: random.choice(list_dir),
            })

            seeder.add_entity(ResponseOs, 100, {
                'ref_os':lambda x: random.choice(list_os),
                })

            inserted_pks = seeder.execute() 
            print (inserted_pks)