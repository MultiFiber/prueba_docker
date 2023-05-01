from django.db import models
from utils.models import BaseModel
from operador.models import Operator
from django.db.models.signals import post_save
from userapp.models import UserApp


class OperatorSetting(BaseModel):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    config   = models.JSONField(null=True, blank=True)

    def __str__(self):
        return "Setting> " + str(self.operator.name)

    def get_keys_config(self):
        if self.config:
            return str(list(self.config.keys()))
        return "Faltan configs, corregir o setear con config automatica"

    class Meta:
        db_table = "operator_setting"
      

class KeyValueOperator(BaseModel):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    name     = models.CharField(max_length=50, null=False, blank=False)
    value    = models.JSONField(null=False, blank=False)

    def __str__(self):
        return "KeyValueOperator> " + str(self.operator.name)

    class Meta:
        verbose_name = 'KeyValueOperator'
        verbose_name_plural = "KeyValuesOperator"



class KeyValueUser(BaseModel):
    user = models.ForeignKey(UserApp, on_delete=models.CASCADE)
    config  = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.user.name)

    class Meta:
        verbose_name = 'KeyValueUser'
        verbose_name_plural = "KeyValuesUser"

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class KeyValueSystem(BaseModel):
    name  = models.CharField(max_length=50, null=False, blank=False)
    value = models.JSONField(null=False, blank=False)

    def __str__(self):
        return "KeyValueSystem> " + str(self.ID)

    class Meta:
        verbose_name = 'KeyValueSystem'
        verbose_name_plural = "KeyValuesSystem"


def generate_setting(sender, instance, **kwargs):

    if 'created' in kwargs and kwargs['created'] is True:
        qs = KeyValueSystem.objects.filter(name='default_conf_for_operators')
        if qs.count() > 0:
            default_conf = qs.last().value
        else:
            default_conf = {}

        OperatorSetting.objects.create(operator_id=instance.ID,
                                       config=default_conf)

post_save.connect(generate_setting, sender=Operator)  