from django.urls import path, re_path, include
from django.views.decorators.cache import cache_page

from rest_framework import routers
from . import views

app_name = 'category'

router_v1 = routers.DefaultRouter()
router_v1.register(r'category', views.CategoryView, 'category')
router_v1.register(r'responseos', views.ResponseOsViewV1, 'responseos-v1')

router_v2 = routers.DefaultRouter()
router_v2.register(r'responseos', views.ResponseOsViewV2, 'responseos-v2')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    #path('v2/', include(router_v2.urls)),
]
