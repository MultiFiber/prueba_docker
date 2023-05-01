import json

from django.contrib import admin
from django.db.models import JSONField 
from django.forms import widgets

from utils.admin import BaseAdmin
from .models import OperatorSetting, KeyValueOperator, KeyValueSystem, KeyValueUser


class PrettyJSONWidget(widgets.Textarea):

   def format_value(self, value):
      try:
         value = json.dumps(json.loads(value), indent=3, sort_keys=True)
         # these lines will try to adjust size of TextArea to fit to content
         row_lengths = [len(r) for r in value.split('\n')]
         self.attrs['rows'] = min(max(len(row_lengths) + 2, 20), 40)
         self.attrs['style'] = """
font-family: Consolas, Monaco, monospace;
font-size: 10pt;
scrollbar-width: thin;
tab-size: 4;
display: block;
overflow-x: auto;
padding: 1em;
background: #3f4233;
color: #f8f8f2;"""
         self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 140)
         return value
      except Exception as e:
         return super(PrettyJSONWidget, self).format_value(value)


@admin.register(OperatorSetting)
class OperatorSettingAdmin(BaseAdmin):
   list_filter = ('operator',)
   list_display = ('get_operador_id', 'operator','get_keys_config')
   search_fields =  ('operator__name',) 

   def get_operador_id(self, obj):
      return obj.operator.ID

   formfield_overrides = {
      JSONField: {'widget': PrettyJSONWidget}
   }



@admin.register(KeyValueOperator)
class KeyValueOperatorAdmin(BaseAdmin):
   list_filter = ('operator',)
   list_display = ('operator','name','value')
   search_fields =  ('operator__name','name') 

   formfield_overrides = {
      JSONField: {'widget': PrettyJSONWidget}
   }



@admin.register(KeyValueSystem)
class KeyValueSystemAdmin(BaseAdmin):
   list_display = ('name','value')
   search_fields = ('name',) 

   formfield_overrides = {
      JSONField: {'widget': PrettyJSONWidget}
   }


@admin.register(KeyValueUser)
class KeyValueUserAdmin(BaseAdmin):
   list_display = ('user','config')
   search_fields =  ('user__name',)
   formfield_overrides = {
      JSONField: {'widget': PrettyJSONWidget}
   }      