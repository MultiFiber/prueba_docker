from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.conf import settings
from simple_history import register
from django.contrib.postgres import indexes
from utils.models import BaseModel

#crear choises para listar los tipos de direcciones
#*Mientras más cercano a 0 es una localización más alejada 
dir_type = [
    (0,  'País'),
    (1,  'Region'),
    (2,  'Estado'),
    (3,  'Municipio'),
    (4,  'Parroquia'),
    (5,  'Comuna'),
    (6,  'Distrito'),
    (7,  'Calle'),
    (8,  'Avenida'),
    (9,  'Cuadra'),
    (10, 'Carretera'),
    (11, 'Diagonal'),
    (12, 'Transversal'),
    (13, 'locacion calle'),
    (14, 'Continente'),
    (15, 'Quinta'),
    (16, 'Torre'),
    (17, 'Piso'),
    (18, 'Locacion completa'),   
    (19, 'Manzana'),
    (20, 'lote'),
    (20, 'poblado'),
]

building_type = [
    (0,'edificio'),
    (1,'casa'),
    (2,'puente'),
    (3,'centro comercial'),
]

class Direction(MPTTModel):

    name = models.CharField(max_length=200)
    iso = models.CharField(max_length=6, null=True, blank=True)
    dirtype = models.IntegerField(choices=dir_type)
    buildingtype = models.IntegerField(choices=building_type, null=True, blank=True)
    parent  = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    #format coordinates {"latitude": -33, "longitude": -70}
    coordinates =  models.JSONField(default=dict, blank=True)
    full_direction = models.CharField(max_length=200, blank=True, null=True)
    #search_vector = pg_search.SearchVectorField(null=True)


    #BaseModel
    deleted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='%(app_label)s_%(class)s_creator'
    )
    #Indicates user who updated instance
    updater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='%(app_label)s_%(class)s_updater'
    )

    class Meta:
        verbose_name='Direction'
        verbose_name_plural='Directions'
        #indexes = [models.Index(fields=['name', 'full_direction']),]
        indexes = [
            indexes.GinIndex(
                fields=['name', 'full_direction'],
                name="busqueda_direccion_1",
            ),
        ]


    class MPTTMeta:
        order_insertion_by = ['dirtype']

    def __str__(self):
        return self.name
    
    def get_text_history(self, updater, change, change_aux):

        if change.field == 'dirtype':
            return f"El usuario {updater} modifico el tipo de dirección de {dir_type[change.old][1]} a {dir_type[change.new][1]}."
    
        if change.field == 'buildingtype':
            return f"El usuario {updater} modifico el tipo de locación de {building_type[change.old][1]} a {building_type[change.new][1]}."
        
        return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        qs = self.get_ancestors()
        self.full_direction = ", ".join([x.name for x in qs] + [self.name])

        super().save(*args, **kwargs)

register(Direction)



class GoogleGeocodeLatlng(BaseModel):
    result = models.JSONField()
    name   = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.management_cache()
        return super().save(*args, **kwargs)


class GoogleGeocodeAddrees(BaseModel):
    result = models.JSONField()
    name   = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.management_cache()
        return super().save(*args, **kwargs)            