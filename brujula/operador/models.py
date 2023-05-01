from django.db import models
from utils.models import BaseModel
from direction.models import Direction

STATUS_CHOICES = (
    (1, 'Activo'),
    (2, 'Inactivo'),
)

class Operator(BaseModel):
    name = models.CharField(max_length=50)
    operator_code = models.CharField(max_length=25, null=True, blank=True)
    country = models.ForeignKey('direction.Direction', on_delete=models.CASCADE)
    email = models.CharField(max_length=255,null=True,blank=True)
    logo =  models.ImageField(null=True,blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    social_networks = models.JSONField(null=True, blank=True)
    web_site = models.TextField(null=True, blank=True)
    additional_information = models.TextField(null=True, blank=True)
    coverage = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def get_text_history(self, updater, change, change_aux):

        if change.field == 'status':
            return f"El usuario {updater} modifico el status del operador {STATUS_CHOICES[change.old][1]} a {STATUS_CHOICES[change.new][1]}."
    
        if change.field == 'country':
            country = Direction.objects.get(id=change.old)
            return f"El usuario {updater} modifico la dirección de {country.name} a {self.country.name}"
        
        if change.field == 'country':
            country = Direction.objects.get(id=change.old)
            return f"El usuario {updater} modifico la dirección de {country.name} a {self.country.name}"
        
        return None
        
    class Meta:
        verbose_name='Operator'
        verbose_name_plural='Operators'




