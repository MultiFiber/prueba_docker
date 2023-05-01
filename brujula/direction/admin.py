from django.contrib import admin
from .models import Direction, GoogleGeocodeLatlng, GoogleGeocodeAddrees
from utils.admin import BaseAdmin

@admin.register(Direction)
class ClassAdmin(BaseAdmin):
   list_filter = ('dirtype',)
   search_fields = ("name",)
   list_display = ('id', 'name','dirtype','parent', 'full_direction')
   readonly_fields = ('id', 'created','updated')
   autocomplete_fields = ['parent']



@admin.register(GoogleGeocodeLatlng)
class ClassAdmin(BaseAdmin):
   search_fields = ("name",)
   list_display = ('ID', 'name',)


@admin.register(GoogleGeocodeAddrees)
class ClassAdmin(BaseAdmin):
   search_fields = ("name",)
   list_display = ('ID', 'name',)   