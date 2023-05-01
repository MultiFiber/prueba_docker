from django.contrib import admin
from .models import Technician, TechnicianPic, Schedule, Disponibility, Absence, Holiday
from utils.admin import BaseAdmin


class TechnicianAdmin(BaseAdmin):
   list_filter = ('operator', 'status', 'id_number')
   list_editable = ('is_supervisor',)
   list_display = ('ID', 'name', 'operator','user', 'is_supervisor', 'supervisores')

   def supervisores(self, obj):
      return ", ".join([str(x) for x in obj.supervised_by.all()])


   def get_list_display(self, request):
      default_list_display = super().get_list_display(request)
      if request.user.is_superuser:
         list_display = ('ID', 'name', 'user', 'is_supervisor', 'supervisores')
         return list_display
      return default_list_display


admin.site.register(Technician, TechnicianAdmin)

class TechnicianPicAdmin(BaseAdmin):
   list_filter = ('owner_tech', 'caption')
   list_display = ('ID', 'caption', 'owner_tech')

admin.site.register(TechnicianPic, TechnicianPicAdmin)

class TechnicianSchedule(BaseAdmin):
   list_select_related = ['technician',]
   list_filter = ('schedule_start_date', 'schedule_end_date', 'disponibility')
   list_display = ('ID', 'schedule_start_date', 'schedule_end_date', 'technician')

admin.site.register(Schedule, TechnicianSchedule)

class DisponibilityAdmin(BaseAdmin):
   list_filter = ('schedule_status', 'dir', 'schedule_day')
   list_display = ('ID', 'schedule_day', 'schedule_status', 'dir')

admin.site.register(Disponibility, DisponibilityAdmin)

class AbsenceAdmin(BaseAdmin):
   list_filter = ('operator',  'status')
   list_display = ('ID', 'operator', 'status', 'time_start','time_end')

admin.site.register(Absence, AbsenceAdmin)

class HolidayAdmin(BaseAdmin):
   list_filter = ('name', 'day', 'status')
   list_display = ('ID', 'name', 'day', 'status')

admin.site.register(Holiday, HolidayAdmin)

