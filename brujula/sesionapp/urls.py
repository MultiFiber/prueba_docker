from django.urls import  path, include
from rest_framework import routers
from .views import  SessionViewSet

router = routers.DefaultRouter()
router.register(r'history-session', SessionViewSet, 'historysession')

urlpatterns = [
    path('v1/', include(router.urls)),
]
"""urlpatterns = [
    path('v1/history-session',SessionViewSet.as_view({'get': 'historysession'})),
    
]"""