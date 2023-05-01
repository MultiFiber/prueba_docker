from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import UserApp,ActionPerm, ActionForUser
from utils.admin import BaseAdmin
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.models import Token


class UserappAdmin(admin.ModelAdmin):
   list_filter = ('name', 'last_name', 'email', 'phone')
   list_display = ('name', 'last_name', 'email', 'phone')
   
   def save_model(self, request, obj, form, change):
      if obj.password.startswith('pbkdf2'):
         obj.password=obj.password
      else:
         obj.set_password(obj.password) 
      super().save_model(request, obj, form, change)


@admin.register(ActionPerm)
class ActionPermAdmin(admin.ModelAdmin):
   list_display = ('name', 'description')
   search_fields = ('name',)

@admin.register(ActionForUser)
class ActionForUserAdmin(admin.ModelAdmin):
   list_display = ('action', 'extra_value', 'for_user',)
   autocomplete_fields = ('action',)





admin.site.register(UserApp, UserappAdmin)
admin.site.register(Permission)
admin.site.register(ContentType)




class SecondAdminSite(AdminSite):
    site_header = "Brujula Admin"
    site_title = "Brujula Admin Portal"
    index_title = "Welcome to Brujula Portal"


brujula_second_admin = SecondAdminSite(name='event_admin')
brujula_second_admin.register(UserApp)


class TokenAdmin(BaseAdmin):
   list_display = ('user','key')
   #list_editable = ('key',)
   readonly_fields = ()

brujula_second_admin.register(Token, TokenAdmin)
