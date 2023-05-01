from datetime import datetime

from django import forms
from django.db import models
from django.db.models.signals import post_save
from django.core.cache import cache
from django.contrib.postgres.search import SearchVector

from utils.models import BaseModel
from tecnico.models import Technician, Disponibility, schedule_days
from operador.models import Operator
from category.models import Category
from ostype.models import Ostype

from direction.models import Direction

DOCUMENTS_CHOICES = (
    (0,'DNI'),
    (1,'RUT'),
    (2,'RUC'),
)

class Client(BaseModel):
    """
    Modelo para manejar datos del cliente.
    Va asociado a la OS, cuando el ISP no tiene sistema propio
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_type = models.SmallIntegerField(choices=DOCUMENTS_CHOICES) 
    document_number = models.CharField(max_length=255) 
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    service_number = models.CharField(max_length=20)
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, null=True, blank=True)
    direction_text = models.TextField()
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
    def get_text_history(self, updater, change, change_aux):

        if change.field == 'direction':
            direction = Direction.objects.get(id=change.old)
            return f"El usuario {updater} modifico la dirección de {direction.name} a {self.direction.name}."
    
        if change.field == 'operator':
            operador = Operator.objects.get(ID=change.old)
            return f"El usuario {updater} modifico el operadpr de {operador.name} a {self.operator.name}."
        
        return None

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'



def find_directions_client_sender(sender, instance, **kwargs):

    if instance.direction == '' or instance.direction==None:

        #Comienza la busqueda
        if instance.operator.country.iso.lower() == 've':
            parts = instance.direction_text.lower().split(',')
            #Modo A 1, Pais, estado, municipio
            if len(parts) == 3:
                municipio = Direction.objects.filter(name=parts[2])
                if municipio.count() > 0:
                    instance.direction = municipio
                else:
                    #Modo A 2, Municipio, estado, parroquia
                    municipio = Direction.objects.filter(name=parts[0])
                    if municipio.count() > 0:
                        instance.direction = municipio

            if len(parts) == 4:
                parroquia = Direction.objects.filter(name=parts[3])
                if parroquia.count() > 0:
                    instance.direction = parroquia

        print ('algo ',instance.direction, sep=' - ')
        if instance.direction == '' or instance.direction==None:
           
            print ('por busqueda completa')
            mi_search = Direction.objects.annotate(
                        search=SearchVector('name', 'full_direction'))\
                        .filter(search=instance.direction_text).only('id')

            print (mi_search.query)
            instance.direction = mi_search.last()


        if instance.direction == '' or instance.direction==None:
            print ('sin resultados')
            try:
                _d = Direction.objects.get(name='otra')
            except Exception as e:
                _d = Direction.objects.create(name='otra', dirtype=1)
            instance.direction = _d

        # Nuevamente verificar sino existe dirección
        # https://docs.djangoproject.com/en/4.1/ref/contrib/postgres/search/
        
        post_save.disconnect(find_directions_client_sender, sender=sender)
        instance.save()
        post_save.connect(find_directions_client_sender, sender=sender)



post_save.connect(find_directions_client_sender, sender=Client)


class OperatorPlans(BaseModel):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE) 
    tradename = models.CharField(max_length=255)
    technology = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.tradename)

    class Meta:
        verbose_name_plural = 'Planes de operador'
        verbose_name = 'Plan del operador'


status = (
    (0, 'Agendada'),
    (1, 'En desplazamiento'),
    (2, 'En atendimiento'),
    (3, 'Pausada'),
    (4, 'En espera del cliente'),
    (5, 'Cancelada'),
    (6, 'No se pudo instalar'),
    (7, 'Por reagendar'),
    (8, 'Finalizada'),
)


class Os(BaseModel):
    status = models.IntegerField(choices=status, default=0)
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    ostype = models.ForeignKey('ostype.Ostype', on_delete=models.CASCADE) #Redundante?
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    technology = models.CharField(max_length=20)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE) #todo: posible elimincación
    sequential_id = models.IntegerField(null=True, blank=True)
    disponibility_hours = models.OneToOneField('tecnico.Disponibility', on_delete=models.CASCADE,blank=True,null=True)

    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, null=True, blank=True)
    
    plan_id = models.IntegerField(null=True, blank=True) # Sistema externo
    user_id = models.IntegerField(null=True, blank=True) # Sistema externo

    plan_brujula = models.ForeignKey(OperatorPlans, on_delete=models.CASCADE, null=True, blank=True)
    user_brujula = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.original_status = self.status

    def __str__(self):
        if hasattr(self, 'client'):
            return f"{self.ID} {self.technician.name} > {self.client.first_name}"    
        return f"{self.ID} {self.technician.name} - {self.ostype.name}"

    def _validate_change(self):

        if self.deleted == False:

            new = self.status
            old = self.original_status

            if old == 0 and new != old:#Agendada
                if new != 1 and new != 2 and new != 3 and new != 4:
                    raise forms.ValidationError(
                        'El nuevo valor no es permitido')

            elif old == 1 and new != old:  # desplazamiento
                if new != 2 and new != 3 and new != 4:
                    raise forms.ValidationError(
                        'El nuevo valor no es permitido')

            elif old == 2 and new != old:  # atendimiento
                if new != 6 and new != 8 and new != 3:
                    raise forms.ValidationError(
                        'El nuevo valor no es permitido')

            elif old == 3 and new != old:  # pausada
                if new != 2 and new != 5 and new != 7 and new != 1:
                    raise forms.ValidationError(
                        'El nuevo valor no es permitido')

            
            elif old == 4 and new != old:#en espera
                if new != 2 and new != 3 and new != 7:
                    raise forms.ValidationError('El nuevo valor no es permitido')

            
            elif old == 5 and new != old:#cancelada
                if new != old:
                    raise forms.ValidationError(
                        'El nuevo valor no es permitido')

                
            elif old == 6 and new != old:#no se pudo instalar
                if new != old:
                    raise forms.ValidationError('El nuevo valor no es permitido')

            
            elif old == 7 and new != old:#reagendar
                if new != 0:
                    raise forms.ValidationError('El nuevo valor no es permitido')

            
            elif old == 8 and new != old:#finalizado
                if new != old:
                    raise forms.ValidationError('El nuevo valor no es permitido')

    def _validate_technician(self):
        if self.technician.status != 0:
            #Emitir alerta
            raise forms.ValidationError('El tecnico no esta activo')

    def to_seconds(self,hora):
        formato = "%H:%M:%S"
        if type(hora)==str:
            hora = datetime.strptime(hora, formato)
        hora = hora.strftime(formato)
        lista = hora.split(":")
        hh=int(lista[0])*3600
        mm=int(lista[1])*60
        ss=int(lista[2])
        suma = hh + mm + ss
        return suma

    def subtract(self,hora_1,hora_2):
        if hora_1 < hora_2:
            swap = hora_2
            hora_2 = hora_1
            hora_1 = swap
        resta = hora_1 -hora_2
        return resta

    def to_hh_mm_ss(self,segundos):
        hor = (segundos / 3600)
        min = ((segundos - hor * 3600) / 60)
        seg = segundos - (hor * 3600 + min * 60) 
        if hor < 10:
            hor = f'0{int(hor)}'
        else:
            hor = f'{int(hor)}'
        if min < 10:
            min = f'0{int(min)}'
        else:
            min = f'{int(min)}'
        if seg < 10:
            seg = f'0{int(seg)}'
        else:
            seg = f'{int(seg)}'
        return f"{hor}:{min}:{seg}"

    def subtract_availability(self):
        d = Disponibility.objects.get(ID=self.disponibility_hours.father.ID)
        hora_1 = self.to_seconds(d.hours_unassigned)
        hora_2 = self.to_seconds(self.disponibility_hours.hours_unassigned)
        if hora_2 < hora_1:
            d.hours_unassigned = self.to_hh_mm_ss(self.subtract(hora_1,hora_2))
            d.save()

    def _validate_disponibility(self):
        
        if self.disponibility_hours.schedule_status != 0 and self.ID == None:
            raise forms.ValidationError('La disponibilidad es invalida')
        elif self.disponibility_hours.schedule_status == 0: #* cambia el estado de la disponibilidad una vez se escoge
            self.disponibility_hours.schedule_status = 1
            self.disponibility_hours.save()
    
    def _validate_dir(self):
        #Se debe mejorar esta validación
        if self.disponibility.dir.dirtype < self.operator.country.dirtype:
            raise forms.ValidationError('La dirección está fuera del alcance del operador')
    
    def _validate_sequential_id (self):
        id = Os.objects.filter(operator=self.operator).count()+1
        self.sequential_id = id 

    def get_text_history(self, updater, change, change_aux):

        if change.field == 'status':
            return f"{updater} coloco la orden de servicio de {status[change.old][1]} a {status[change.new][1]}."

        if change.field == 'disponibility_hours':
            disponibility_old = Disponibility.objects.get(ID=change.old)
            disponibility_new = Disponibility.objects.get(ID=change.new)
            return f"{updater} cambio la disponibilidad de la orden de servicio de {schedule_days[disponibility_old.schedule_day][1]} {disponibility_old.schedule_start_time.strftime('%H:%M')}-{disponibility_old.schedule_end_time.strftime('%H:%M')} a {schedule_days[disponibility_new.schedule_day][1]} {disponibility_new.schedule_start_time.strftime('%H:%M')}-{disponibility_new.schedule_end_time.strftime('%H:%M')}."

        if change.field == 'ostype':
            os_type_old = Ostype.objects.get(ID=change.old)
            os_type_new = Ostype.objects.get(ID=change.new)
            return f"{updater} modifico el tipo de orden de servicio de {os_type_old.name} a {os_type_new.name}."

        if change.field == 'category':
            category_old = Category.objects.get(ID=change.old)
            category_new = Category.objects.get(ID=change.new)
            return f"{updater} modifico la categoria de {category_old.name} a {category_new.name}."
        
        if change.field == 'technician':
            technician = Technician.objects.get(ID=change.old)
            return f"{updater} modifico el técnico de {technician.name} {technician.last_name} a {self.technician.name} {self.technician.last_name}."
        
        if change.field == 'plan_brujula':
            plan = OperatorPlans.objects.get(ID=change.old)
            return f"{updater} modifico el plan de {plan.tradename} a {self.plan_brujula.tradename}."

        if change.field == 'user_id':
            return f"{updater} modifico el id del usuario de {change.old} a {change.new}."
        
        if change.field == 'user_brujula':
            client = Client.objects.get(ID=change.old)
            return f"{updater} modifico el cliente de {client.first_name} {client.last_name} a {self.user_brujula.first_name} {self.user_brujula.last_name}."
        
        if change.field == 'direction':
            direction_old = Direction.objects.get(id=change.old)
            direction_new = Direction.objects.get(id=change.new)
            return f"{updater} modifico la dirección de {direction_old.name} a {direction_new.name}."

        return None


    def save(self, *args, **kwargs):

        # if (self.user_id=='' or self.user_id==' ' or self.user_id=='0' or self.user_id==None)\
        #     and not hasattr(self, 'client'):
        #     raise forms.ValidationError('No existe cliente de OS')

        self._validate_technician()
        
        # Validacion pendiente.
        #self._validate_disponibility()

        if self.ID != None : 
            self._validate_change()
        else:
            self._validate_sequential_id()
            self.subtract_availability()
        super(Os, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Os'
        verbose_name_plural = "OS's"

class OsPic(BaseModel):
    photo = models.ImageField(upload_to='photos')
    caption = models.CharField(max_length=255)
    owner_os = models.ForeignKey(Os, on_delete=models.CASCADE, related_name='owner_os')

    def __str__(self):
        return self.caption

    def management_cache(self):
        print ('Model cache {}'.format(self.__class__.__name__))
        #Delete cache
        cache.delete( f"history_v1_{self.__class__.__name__}_{self.ID}" )
        cache.delete( f'view_v1_{self.__class__.__name__}_Full_{self.ID}')
        cache.delete( f'get_object_v1_{self.__class__.__name__}_{self.ID}')
        cache.delete( f'model_v1_{self.__class__.__name__}_{self.ID}')

    def get_text_history(self, updater, change, change_aux):

        if change.field == 'photo':
            return f"{updater} cambió la foto de la orden de servicio."
        
        if change.field == 'owner_os': 
            os = Os.objects.get(ID=change.old)
            return f"{updater} cambió la orden de servicio a la que pertenece de #{os.sequential_id} a #{self.owner_os.sequential_id}."
        
        return None
            
    def save(self, *args, **kwargs):
        super(OsPic, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'OSPic'
        verbose_name_plural = 'OSPics'

medio_desplazamiento = (
    (0, 'Vehiculo'),
    (1, 'Otro'),
)

class Displacement(BaseModel):

    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    direction_init = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='dir1')
    direction_final = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='dir2')
    km_init = models.IntegerField()
    km_final = models.IntegerField(null=True,blank=True)
    os = models.ForeignKey('Os', on_delete=models.CASCADE)
    medio_desplazamiento = models.IntegerField(choices=medio_desplazamiento, default=0)
    estimated_time = models.TimeField(null=True, blank=True)
    displacement_time = models.TimeField(null=True, blank=True)
    sequential_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.os)

    def _validate_sequential_id (self):
        id = Displacement.objects.filter(os__operator=self.os.operator).count()+1
        self.sequential_id = id

    def get_text_history(self, updater, change, change_aux):

        if change.field == 'os':
            os = Os.objects.get(ID=change.old)
            return f"{updater} cambio el dsplazamiento a la orden de servicio #{os.sequential_id} a {self.os.sequential_id}."

        if change.field == 'medio_desplazamiento':
            return f"{updater} modifico el tipo de orden de servicio de {medio_desplazamiento[change.old][1]} a {medio_desplazamiento[change.new][1]}."
        
        return None

    class Meta:
        verbose_name = 'Displacement'
        verbose_name_plural = 'Displacements'

    def save(self, *args, **kwargs):
        if self.ID == None : #Case update
            self._validate_sequential_id()
        super(Displacement, self).save(*args, **kwargs)

    
class TripSummary(BaseModel):

    date = models.DateField(auto_now_add=True, null=True, blank=True)
    time = models.TimeField(auto_now_add=True, null=True, blank=True)
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    status_init = models.IntegerField(choices=status, null=True, blank=True)
    status_final = models.IntegerField(choices=status, null=True, blank=True)
    km_initial = models.IntegerField(null=True,blank=True)
    km_final = models.IntegerField(null=True,blank=True)
    nro_os = models.ForeignKey('Os', on_delete=models.CASCADE)
    nro_displacement = models.ForeignKey('Displacement', on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return str(self.nro_os)
    
    def get_text_history(self, updater, change, change_aux):

        if change.field == 'technician':
            technician = Technician.objects.get(ID=change.old)
            return f"{updater} modifico el técnico de {technician.name} {technician.last_name} a {self.technician.name} {self.technician.last_name}."

        if change.field == 'status_init':
            return f"{updater} modifico el status inicial de {status[change.old][1]} a {status[change.new][1]}."
        
        if change.field == 'status_final':
            return f"{updater} modifico el status inicial de {status[change.old][1]} a {status[self.status_final][1]}."
        
        if change.field == 'nro_os':
            os = Os.objects.get(ID=change.old)
            return f"{updater} cambio el dsplazamiento a la orden de servicio #{os.sequential_id} a #{self.nro_os.sequential_id}."

        if change.field == 'nro_displacement':
            displacement = Displacement.objects.get(ID=change.old)
            return f"{updater} cambio el dsplazamiento de #{displacement.sequential_id} a #{self.nro_displacement.sequential_id}."

        return None

    class Meta:
        verbose_name = 'Trip Summary'
        verbose_name_plural = 'Trip Summarys'