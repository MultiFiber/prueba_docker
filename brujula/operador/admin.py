from django.contrib import admin
from .models import Operator
from utils.admin import BaseAdmin
from operator_setting.models import OperatorSetting
from django.forms import widgets
from django.db.models import JSONField


class PrettyJSONWidget(widgets.Textarea):

   def format_value(self, value):
      try:
         value = json.dumps(json.loads(value), indent=3, sort_keys=True)
         # these lines will try to adjust size of TextArea to fit to content
         row_lengths = [len(r) for r in value.split('\n')]
         self.attrs['rows'] = min(max(len(row_lengths) + 2, 20), 40)
         self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 140)
         return value
      except Exception as e:
         return super(PrettyJSONWidget, self).format_value(value)


class OperatorSAdmin(admin.StackedInline):
    model = OperatorSetting
    extra = 0
    fields = ['config']
    #readonly_fields=('config',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

class OperatorAdmin(BaseAdmin):
    search_fields = ['name','operator_code']
    list_display = ('ID','name', )
    list_filter = ('name', 'operator_code', 'country')
    inlines = [OperatorSAdmin,]

admin.site.register(Operator, OperatorAdmin)