from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.contrib.auth.models import Group
from utils.models import BaseModel
from operador.models import Operator
from django.core.cache import cache

class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('El usuario require un email')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_superuser =True
        user.is_staff =True
        user.save(using=self._db)
        return user
    

status_user = (
    (0,'Activo'),
    (1,'Inactivo'),
)

class UserApp(BaseModel, AbstractBaseUser, PermissionsMixin):
    email =  models.EmailField(max_length=255, unique=True)
    operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True)
    name  = models.CharField(max_length=100, null=True, blank=True)
    last_name  = models.CharField(max_length=100, null=True, blank=True)
    phone =  models.CharField(max_length=20, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    objects = UserManager()
    sequential_id = models.IntegerField(null=True,blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
    def get_text_history(self, updater, change, change_aux):
    
        if change.field == 'operator':
            operador_old = Operator.objects.get(ID=change.old)
            operador_new = Operator.objects.get(ID=change.new)
            return f"{updater} modifico el operador de {operador_old.name} a {operador_new.name}."
        
        return None
    
    def _validate_sequential_id (self):
        id = UserApp.objects.filter(operator=self.operator).count()+1
        self.sequential_id = id 

    def save(self, *args, **kwargs):
        if self.ID == None: 
            self._validate_sequential_id()
        super(UserApp, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name='User'
        verbose_name_plural='Users'



class ActionPerm(models.Model):
    name = models.CharField(max_length=150, primary_key=True)
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

# userapp_change_all_field_all_objects
# userapp_change_all_field_pk_1
# userapp_change_phone_number_all_objets
# tecnichian_create_phone_number_operator_pk_{*}

    class Meta:
        verbose_name='Action Perm'
        verbose_name_plural='Actions Perms'


class ActionForUser(BaseModel):
    action = models.ForeignKey(ActionPerm, on_delete=models.CASCADE)
    extra_value = models.CharField(max_length=10, null=True, blank=True)
    for_user = models.ForeignKey(UserApp, on_delete=models.CASCADE)

    def __str__(self):
        return self.action.name
    
    class Meta:
        verbose_name='Action For User'
        verbose_name_plural='Actions For User'        