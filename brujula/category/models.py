from django.db import models
from utils.models import BaseModel
from django.db.models import JSONField

class Category(BaseModel):

    name = models.CharField(max_length=50)
    duration = models.IntegerField(default=0)
    imgs = JSONField()
    questions = JSONField()
    os_type = models.ForeignKey('ostype.Ostype', on_delete=models.CASCADE)
    description = models.CharField(max_length=50, null=True, blank=True)
    sequential_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def _validate_sequential_id (self):
        id = Category.objects.filter(os_type__operator=self.os_type.operator).count()+1
        self.sequential_id = id 

    def get_text_history(self, updater, change, change_aux):

        if change.field == 'imgs':
            return f"El usuario {updater} modifico la imagen de la categoría."
        
        if change.field == 'questions':
            return f"El usuario {updater} modifico las preguntas de la categoría."
        
        return None
    
    def save(self, *args, **kwargs):
        # self.clean_verificacion()
        if self.ID == None : #Case update
            self._validate_sequential_id()
        super(Category, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name='Category'
        verbose_name_plural='Categorys'
        ordering = ['ID']

#   Modelo de Json imgs
#   {
#   "value": ["imag1","imag2"]
#   }      


#   Modelo de json para question category 
#   {
#   "value": [{question": "Ford","kind: 1},
#             {"question": "Ford","kind: 1},
#             ]
#   }

#   Tipos de respuestas
#   si o no  -> 1
#   texto escrito -> 2

#   Datatable de category retornar según el tipo de respuesta 
#   Hacer validaciones para la estructura del JSON



class ResponseOs(BaseModel):

    ref_os = models.ForeignKey('OS.Os', on_delete=models.CASCADE)
    questions = JSONField()

    def __str__(self):
        return "Respuestas de {}".format(str(self.ref_os))
    
    def get_text_history(self, updater, change, change_aux):

        if change.field == 'questions':
            return f"El usuario {updater} modifico las preguntas."
        
        return None

    class Meta:
        verbose_name='Response Os'
        verbose_name_plural='Responses Os'
        ordering = ['ID']