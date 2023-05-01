from django.contrib import admin
from .models import Category, ResponseOs
from utils.admin import BaseAdmin

# Register your models here.

class CategoryAdmin(BaseAdmin):
   list_filter = ('name', 'duration','os_type',)
   list_display = ('ID', 'name','description','os_type','description')

class ResponseOsAdmin(BaseAdmin):
   list_filter = ('ref_os',)
   list_display = ('ID', 'ref_os','questions')

admin.site.register(Category, CategoryAdmin)
admin.site.register(ResponseOs, ResponseOsAdmin)
