from django.urls import path, include, re_path
from rest_framework import routers
from .views import *

router_v1 = routers.DefaultRouter()
router_v1.register(r'operator-setting', OperatorSettingViewSetV1, 'operator-setting-v1')

router_v2 = routers.DefaultRouter()
router_v2.register(r'operator-setting/(?P<operador>.+)', OperatorSettingViewSetV2, 'operator-setting-v2')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v2/', include(router_v2.urls)),
]