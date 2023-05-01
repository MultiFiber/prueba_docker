from django.contrib import admin
from utils.admin import BaseAdmin
from .models import Os, OsPic, Displacement, TripSummary, Client, OperatorPlans


@admin.register(Client)
class ClientAdmin(BaseAdmin):
   list_filter = ('first_name', 'last_name','phone','email','document_number','service_number', 'direction')
   list_display = ('first_name','last_name','direction','phone','email','document_number','service_number')
   autocomplete_fields = ['direction','operator']
   #raw_id_fields = ("direction", )


@admin.register(OperatorPlans)
class OperatorPlansAdmin(BaseAdmin):
   list_filter = ('operator',)
   list_display = ('tradename', 'technology',)


@admin.register(Os)
class OsAdmin(BaseAdmin):
   #search_fields =  ('owner_os__technician',)  
   list_filter = ('operator','status','ostype')
   list_display = ('ID', 'status','category', 'plan_id', 'plan_brujula',
                  'technology','technician', 'operator','has_fix_user','fix_plan')

   def has_fix_user(self, obj):
      if (obj.user_id=='' or obj.user_id==' ' or obj.user_id=='0' or obj.user_id==None)\
         and not hasattr(obj, 'user_brujula'):
         return 'sin cliente'

      if hasattr(obj, 'user_id') and hasattr(obj, 'client'):
         return '2 clientes'

      return 'OK'

   def fix_plan(self, obj):
      not_has_brujula = not hasattr(obj.plan_brujula, 'ID')
      not_has_id = obj.plan_id=='' or obj.plan_id==' ' or obj.plan_id=='0' or obj.plan_id==None

      if not_has_brujula and not_has_id:
         return 'sin plan'

      if not not_has_brujula and not not_has_id:
         return '2 planes'

      return 'OK'

@admin.register(OsPic)
class OsPicAdmin(BaseAdmin):
   search_fields =  ('owner_os__technician',)   
   list_filter = ('owner_os__operator',)
   list_display = ('ID','photo','caption','owner_os')


@admin.register(Displacement)
class DisplacementAdmin(BaseAdmin):
   #search_fields =  ('os__technician__id_number','os__technician__name','os__technician__last_name',)
   list_filter = ('date', 'os')
   list_display = ('date', 'os')

   def name_technician(self, instance):
      return instance.os.technician.name


@admin.register(TripSummary)
class TripSummaryAdmin(BaseAdmin):
   
   list_filter = ('nro_os','technician','date')
   list_display = ('date','time','nro_os','nro_displacement','status_init','status_final','km_initial','km_final','technician')
