from django.contrib import admin
from django.contrib.messages import constants as messages

class BaseAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    actions = ['change_activation','change_status']
    readonly_fields = ('ID', 'created','updated')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        self.request = request
        return qs

    def change_activation(self, request, queryset):
        model = self.model._meta.verbose_name
        n = queryset.count()
        message = "%(count)d %(model)s cambiadas." % {"count": n ,"model":model}
        self.message_user(request, message, messages.SUCCESS)   
        for item in queryset:
            if item.deleted:
                item.deleted = False
            else:
                item.deleted = True
            item.save()
        return queryset
    change_activation.short_description = 'Cambia el estado de la activacion'


    def change_status(self, request, queryset):
        if hasattr(self.model,'status'):
            model = self.model._meta.verbose_name
            n = queryset.count()
            message = "%(count)d %(model)s cambiadas." % {"count": n ,"model":model}
            self.message_user(request, message, messages.SUCCESS)   
            for item in queryset:

                if item.status:
                    item.status = False
                else:
                    item.status = True
                item.save()
        return queryset
    change_status.short_description = 'Cambia estatus'