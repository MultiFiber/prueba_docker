from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/', include('autenticacion.urls')),
    path('api/', include('category.urls')),
    path('api/', include('operador.urls')),
    path('api/', include('operator_setting.urls')),
    path('api/', include('OS.urls')),
    path('api/', include('ostype.urls')),
    path('api/', include('tecnico.urls')),
    path('api/', include('direction.urls')),
    path('api/', include('userapp.urls')),
    path('report/', include(('report.urls','report'))),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)