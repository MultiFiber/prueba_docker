from django.core.management.base import BaseCommand
from direction.models import Direction
import logging
import requests
import os


logging.getLogger("urllib3").setLevel(logging.WARNING)

urls=[
    'https://pulso.multifiber.cl/api/v1/search-commune/',
    'https://pulso.multifiber.cl/api/v1/search-street/',
    'https://pulso.multifiber.cl/api/v1/search-streetlocation/',
    'https://pulso.multifiber.cl/api/v1/search-tower/',
    'https://pulso.multifiber.cl/api/v1/search-floor/',
    'https://pulso.multifiber.cl/api/v1/search-completelocation/',
]

class Command(BaseCommand):
    help = 'Get directions from Pulso'

    #def add_arguments(self, parser):
        #parser.add_argument('poll_ids', nargs='+', type=int)
    """
    def save_the_status(self, nivel, id_guardar):
        with open('archivo.pulso', 'w') as mi_archivo:
            ### Formato es =
            ### donde guardo  -  id que acaba de guardar de brujula (padre)
            mi_archivo.write(f'{nivel}-{id_guardar}')

        return True

    def read_the_status(self):
        data = None
        try:
            with open('archivo.pulso', 'r') as mi_archivo:
                data = mi_archivo.read()
        except Exception as e:
            return None
        return data 
    
    """


    def get_base_request(self, url):

        #url = os.environ.get("PULSO_URL")
        #headers = {"Authorization": "token {}".format(os.environ.get("PULSO_TOKEN"))}
        headers = {"Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}
        base_url = 'https://pulso.multifiber.cl/api/v1/{}'.format(url)
        r = requests.get(base_url, headers)
        return r

    def get_comunnes(self, data_region, i, region):
        #Commune
        res = requests.get('https://pulso.multifiber.cl/api/v1/search-commune/' + str(data_region[i]['id']))
        if res.status_code == 200:
            data_comunas = res.json()
            for j in range(len(data_comunas)):
                commune = Direction.objects.create(name = data_comunas[j]['name'],
                dirtype=14, buildingtype = None, parent=region)
                print("commune created")
                self.get_street(data_comunas, j, commune)

    def get_street(self, data_comunas, j, commune):
        pong = requests.get('https://pulso.multifiber.cl/api/v1/search-street/' + str(data_comunas[j]['id']))
        if pong.status_code == 200:
            pong = pong.json()
            for k in range(len(pong)):
                street = Direction.objects.create(name = pong[k]['name'],
                dirtype=0, buildingtype = None, parent = commune)
                print('Street created')

    def get_pulso(self, nivel=0, ID=0, Parent=None):
        print(nivel, ID, Parent)
        input("Press Enter to continue...")
        if nivel == len(urls):
            return
        """
        dirtypes = {
            0:6,
            1:14,
            2:0,
            3:0
        }
        """

        r=requests.get(urls[nivel]+str(ID))
        if r.status_code==200:
            r = r.json()
            if len(r) >0:
                for item in r:
                    if Direction.objects.filter(name=item['name']).exists():
                        print('already created')
                        self.get_pulso(Parent=Direction.objects.get(name=item['name']), ID= item['id'], nivel=nivel+1)
                    else:
                        parent = Direction.objects.create(name=item['name'],
                            dirtype=nivel, buildingtype =None, parent=Parent)

                        self.get_pulso(nivel=nivel+1,ID=item['id'],Parent=parent)
                        print('created')
            """           
            if len(r.json()) > 0:
                datos = r.sjon()
                for item in datos:
                    
                    row = Direction.objects.create(name=item['name'],
                    dirtype=dirtypes[nivel], buildingtype = None, parent_id=ID)
                    self.save_the_status(nivel, item['id'])
                    self.get_pulso(nivel+1, ID)

                    print(urls[nivel].split('/')[-1]+'created')
            """

    def get_country(self):
        r = self.get_base_request('country')
        if r.status_code == 200:
            if Direction.objects.filter(name = r.json()["results"][0]['name']).exists():
                print('country alredy exist')
            else:
                country = Direction.objects.create(
                    name = r.json()["results"][0]['name'],
                    dirtype = 6, buildingtype = None, parent=None)
                print("Country Created")
                return country

    """
    def get_region(self, Parent):

            country = Direction.objects.create(
            name = r.json()["results"][0]['name'],
            dirtype = 6, buildingtype = None, parent=None)

            print("Country Created")
            self.save_the_status(0, None)            
            return country.id
    """

    def get_region(self, Parent):
        r = self.get_base_request('region')
        if r.status_code == 200:
            r = r.json()['results']
            for item in r :
                if Direction.objects.filter(name=item['name']).exists():
                    print('region already exist')
                    self.get_pulso(Parent=Direction.objects.get(name=item['name']), ID= item['id'])
                else: 
                    region = Direction.objects.create(
                        name = item['name'],
                        dirtype = 7, buildingtype = None, parent=Parent)
                    print("region created")
                    self.get_pulso(Parent=region, ID = item['id'] )
                
                """
                region = Direction.objects.create(
                name = item['name'],
                dirtype = 16, buildingtype = None, parent=Parent)

                print("region created")
                self.save_the_status(1, item['id'])
                raise Exception(5)
                self.get_pulso(1, item['id'])
                """



    def handle(self, *args, **options):        

        """ 
        #Region
            for i in range(len(r)):
                region = Direction.objects.create(name = r[i]['name'], dirtype = 16, 
                buildingtype = None, parent=country)
                print("Region Created")
                self.get_comunnes(data_region, i, region)
       

        status = self.read_the_status()
        if status:
            nivel, id_nivel = status.split('-')
            print (nivel, id_nivel)
            if nivel == 1:
                self.get_region(id_nivel)
            if nivel == 2:
                self.get_pulso(2, id_nivel)
        else:
            
            country_id = self.get_country()
            region = self.get_region(country_id)
        """

        country = self.get_country()
        self.get_region(country)

        #self.get_pulso(parent=region)

