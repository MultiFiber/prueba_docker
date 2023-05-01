from django.contrib import admin
from django.urls import include, path, re_path
from utils.api_docs import GetMeView, schema_view
from userapp.admin import brujula_second_admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('api/get_me/', GetMeView.as_view()),
    path('grappelli/', include('grappelli.urls')), # grappelli URLS

    #Admin
    path('multifiber_admin/', admin.site.urls),
    path('multifiber_especial_admin/', brujula_second_admin.urls),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  