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
            seeder.add_entity(UserApp, 1)
            seeder.add_entity(Operator, 1)
            seeder.add_entity(Ostype, 1)
            seeder.execute()
 
            list_ostype = [item for item in Ostype.objects.all()]
            seeder.add_entity(Category, 2 , {
                'os_type':lambda x: random.choice(list_ostype),
            })            
            list_operador = [item for item in Operator.objects.all()]
            list_user = [item.ID for item in UserApp.objects.all()]

            seeder.add_entity(Technician, 1, {
                'operator':lambda x: random.choice(list_operador),
                'user_id': lambda x: random.choice(list_user),
            })

            inserted_pks = seeder.execute() 
            print (inserted_pks)