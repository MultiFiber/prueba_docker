from django.contrib import admin
from .models import Ostype
from utils.admin import BaseAdmin

@admin.register(Ostype)
class OstypeClassAdmin(BaseAdmin):
   list_filter = ('operator',)
   list_display = ('ID', 'name','color','operator')
   readonly_fields = [item for item in BaseAdmin.readonly_fields] + ['categories']

   def categories(self, obj):
      return " \n ".join(
         [str(x) + "-" +str(x.ID) for x in obj.category_set.all()]
      )