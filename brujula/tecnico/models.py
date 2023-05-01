from django.db import models
from utils.models import BaseModel
from operador.models import Operator
from category.models import Category
from direction.models import Direction
from django.forms import ValidationError
from django.db.models import JSONField
from datetime import datetime, timedelta
from mptt.models import MPTTModel, TreeForeignKey

documentos = (
    (0, 'pasaporte'),
    (1, 'dni'),
    (2, 'rut'),
    (3, 'cedula'),
    (4, 'pasaporte'),
    (5, 'dni'),
    (6, 'ce'),    
)


status_tecnicos = (
    (0, 'Disponible'),
    (1, 'No disponible'),
    (2, 'En almuerzo'),
    (3, 'Ausente'),
    (4, 'No laborable')       
)

status = [('Estados', status_tecnicos,)]

class Technician(BaseModel):

    birthday = models.DateField()
    id_type = models.IntegerField(choices=documentos)
    id_number = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    status = models.IntegerField(choices=status)
    user = models.OneToOneField(
        'userapp.UserApp',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    device = JSONField(default=dict, blank=True)
    is_supervisor = models.BooleanField(default=False)
    supervised_by = models.ManyToManyField('tecnico.Technician', blank=True)
    sequential_id = models.IntegerField(null=True, blank=True)
    categories = models.ManyToManyField(Category)

    @property
    def full_name(self):
        return f"{self.name} {self.last_name}"

    @property
    def supervidados_obj(self):
        return Technician.objects.filter(supervised_by=self)

    @property
    def supervidados_ids(self):
        return [x[0] for x in Technician.objects.filter(supervised_by=self).values_list('ID')]

    def get_status_diplay(self):
        return status_tecnicos[self.status][1]

    def __str__(self):
        return self.name
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.original_status = self.status
    
    class Meta:
        verbose_name='Technician'
        verbose_name_plural='Technicians'

    # def clean_verificacion(self):
    #     if self.deleted == False:
    #         print('ok')
            
    def _validate_change(self):

        if self.deleted == False:

            new = int(self.status)
            old = int(self.original_status)
            

            if old == 0 and new != old:#Disponible

                if new != 1 and new != 2 and new != 3:
                    raise ValidationError(
                        'El nuevo valor no es permitido')

            elif old == 1 and new != old:  #No disponible
                if new != 0 and new != 3:
                    raise ValidationError(
                        'El nuevo valor no es permitido')

            elif old == 2 and new != old:  # En almuerzo
                if new != 0:
                    raise ValidationError(
                        'El nuevo valor no es permitido')

            elif old == 3 and new != old:  # Ausente
                if new != 0:
                    raise ValidationError(
                        'El nuevo valor no es permitido')

    def _validate_sequential_id (self):
        id = Technician.objects.filter(operator=self.operator).count()+1
        self.sequential_id = id 

    def get_text_history(self, updater, change, change_aux):

        if change.field == 'name':
            return f"El usuario {updater} cambió el nombre  del técnico de {change.old} a {self.name}."
        
        if change.field == 'last_name':
            return f"El usuario {updater} cambió el apellido del técnico de {change.old} a {self.last_name}."

        if change.field == 'birthday':
            return f"El usuario {updater} modifico la fecha de nacimiento del técnico de {change.old} a {change.new}."
        
        if change.field == 'operator':
            operator = Operator.objects.get(ID=change.old)
            return f"El usuario {updater} modifico el operador del técnico de {operator.name} a {change.new}."
        
        if change.field == 'id_number':
            return f"El usuario {updater} modifico el número de documento del técnico de {change.old} a {change.new}."
        
        if change.field == 'id_type':
            return f"El usuario {updater} modifico el tipo de documento del técnico  de {documentos[change.old][1]} a {documentos[change.new][1]}."
        
        if change.field == 'status':
            return f"{updater} modifico el status de técnico de {status_tecnicos[change.old][1]} a {status_tecnicos[change.new][1]}."
        
        return None


    def save(self, *args, **kwargs):
        # self.clean_verificacion()
        if self.ID != None : #Case update
            self._validate_change()
        else:
            self._validate_sequential_id()
        super(Technician, self).save(*args, **kwargs)


class TechnicianPic(BaseModel):
    photo = models.ImageField(upload_to='photos')
    caption = models.CharField(max_length=255)
    owner_tech = models.ForeignKey(Technician, on_delete=models.CASCADE, related_name='owner_tech')

    def __str__(self):
        return self.caption
    
    class Meta:
        verbose_name='TechnicianPic'
        verbose_name_plural='TechnicianPics'


schedule_status = (
    (0, 'Disponible'),
    (1, 'No disponible'),
    (2, 'En almuerzo'),
    (3, 'Ausente'),
)

schedule_days = (
    (0, 'Lunes'),
    (1, 'Martes'),
    (2, 'Miercoles'),
    (3, 'Jueves'),
    (4, 'Viernes'),    
    (5, 'Sabado'),
    (6, 'Domingo'),
)


class Disponibility(BaseModel):

    schedule_status = models.IntegerField(choices=schedule_status)
    schedule_day = models.IntegerField(choices=schedule_days)
    dir = models.ForeignKey('direction.Direction', on_delete=models.CASCADE)
    date = models.DateField(null=True,blank=True)
    schedule_start_time = models.TimeField()
    schedule_end_time = models.TimeField()
    father  = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    hours_unassigned = models.TimeField(null=True, blank=True)

    def to_seconds(self,hora):
        formato = "%H:%M:%S"
        hora = hora.strftime(formato)
        lista = hora.split(":")
        hh=int(lista[0])*3600
        mm=int(lista[1])*60
        ss=int(lista[2])
        suma = hh + mm + ss
        return suma

    def to_hh_mm_ss(self,segundos):
        number = int(segundos)
        hor = (number / 3600)
        if number < 3600:
            min = hor * 60
        else:
            if int(hor) > hor:
                min = (int(hor) - hor) * 60
            else:
                min = (hor - int(hor)) * 60
        if hor < 10:
            hor = f'0{int(hor)}'
        else:
            hor = f'{int(hor)}'
        if min < 10:
            min = f'0{int(min)}'
        else:
            min = f'{int(min)}'
        seg = "00"
        return f"{hor}:{min}:{seg}"

    def _unassigned_hours(self):
        hora_1 = self.to_seconds(self.schedule_start_time)
        hora_2 = self.to_seconds(self.schedule_end_time)
        if hora_1 < hora_2:
            swap = hora_2
            hora_2 = hora_1
            hora_1 = swap
        resta = hora_1 - hora_2
        self.hours_unassigned = self.to_hh_mm_ss(resta)


    def save(self, *args, **kwargs):
        if self.ID == None:
            self._unassigned_hours()
        super(Disponibility, self).save(*args, **kwargs)

    def __str__(self):
        return "{}-{} | {}-{}".format(self.ID, self.get_schedule_day_display(),
                                      self.schedule_start_time, self.schedule_end_time)
    
    class Meta:
        verbose_name='Disponibility'
        verbose_name_plural='Disponibilitys'



holiday_type = (
    (0, 'religioso'),
    (1, 'civil')
)

holiday_status = (
    (0, 'Activo'),
    (1, 'Inactivo'),
)

class Holiday(BaseModel):

    day = models.DateTimeField()
    name = models.CharField(max_length=30) 
    status = models.IntegerField(choices=holiday_status)
    holiday_type = models.IntegerField(choices=holiday_type)
    operator = models.ForeignKey('operador.Operator', on_delete=models.CASCADE)
    sequential_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def _validate_sequential_id (self):
        id = Holiday.objects.filter(operator=self.operator).count()+1
        self.sequential_id = id 
    
    def save(self, *args, **kwargs):
        if self.ID == None:
            self._validate_sequential_id()
        super(Holiday, self).save(*args, **kwargs)
        
    class Meta:
        verbose_name='Holiday'
        verbose_name_plural='Holidays'


absence_status = (
    (0, 'Pendiente'),
    (1, 'Aprobada'),
    (2, 'Rechazada'),
)

absence_type = (
    (0, 'Almuerzo'),
    (1, 'Permiso'),
    (2, 'Día Libre'),

)

class Absence(BaseModel):

    sequential_id = models.IntegerField(null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    status = models.IntegerField(choices=absence_status)
    time_start = models.DateTimeField(blank=True, null=True)
    time_end = models.DateTimeField(blank=True, null=True)
    type = models.IntegerField(choices=absence_type,default=0)
    # schedule_day = models.IntegerField(choices=schedule_days)

    def __str__(self):
        return self.operator.name
    
    def _validate_sequential_id (self):
        id = Absence.objects.filter(operator=self.operator).count()+1
        self.sequential_id = id

    def save(self, *args, **kwargs):
        if self.ID == None:
            self._validate_sequential_id()
        super(Absence, self).save(*args, **kwargs)

    class Meta:
        verbose_name='Absence'
        verbose_name_plural='Absences'


class Schedule(BaseModel):

    schedule_start_date = models.DateField()
    schedule_end_date = models.DateField(null=True, blank=True)
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)#* CAmbiar FK a MtM 
    disponibility = models.ManyToManyField(Disponibility)
    absence = models.ManyToManyField(Absence)
    Holiday = models.ManyToManyField(Holiday) #* Posible cambio de relación en un futuro 

    def __str__(self):
        return self.technician.name
        
    class Meta:
        verbose_name='Schedule'
        verbose_name_plural='Schedules'