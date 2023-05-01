from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from datetime import datetime
from django.contrib.auth import get_user_model 
from django.core.cache import cache

#User = get_user_model()

class BaseModel(models.Model):

    """

        Class define models or tables on DB.
    
    """
    #Indicates unique ID of instance
    ID: int = models.AutoField(primary_key=True)
    #Indicates if instance is deleted
    deleted: bool = models.BooleanField(default=False)
    #Save historical changes of instance
    history = HistoricalRecords(inherit=True)
    #Indicates datetime was created instance
    created: datetime = models.DateTimeField(auto_now_add=True)
    #Indicates last datetime was update instance
    updated:datetime = models.DateTimeField(auto_now=True)
    #Indicates user who created instance
    creator: int = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='%(app_label)s_%(class)s_creator'
    )
    #Indicates user who updated instance
    updater: int = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='%(app_label)s_%(class)s_updater'
    )

    def management_cache(self):
        print ('Model cache {}'.format(self.__class__.__name__))
        #Delete cache
        cache.delete( f"history_v1_{self.__class__.__name__}_{self.ID}" )
        cache.delete( f'view_v1_{self.__class__.__name__}_Full_{self.ID}')
        cache.delete( f'get_object_v1_{self.__class__.__name__}_{self.ID}')
        cache.delete( f'model_v1_{self.__class__.__name__}_{self.ID}')

        #Save new cache
        cache.set(f"model_v1_{self.__class__.__name__}_{self.ID}", self.__dict__, settings.CACHES_TIMES['max'])
        
    def delete(self, *args, **kwargs):

        """

            This funtion, overwrites delete method. Prevent delete instance and only set 'deleted' field to 'True'

        """

        self.deleted: bool = True
        self.save()

    def real_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        
    def save(self, *args, **kwargs):

        self.clean()
        self.management_cache()
        super().save( *args, **kwargs)

    class Meta:

        abstract: bool = True

