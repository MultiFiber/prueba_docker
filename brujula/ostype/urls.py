from email.mime import base
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import  OstypeViewSet

router = DefaultRouter()
router.register('ostype', OstypeViewSet, basename='ostype')

urlpatterns = [

    #path('v1/ostype/history/<int:id>', OstypeViewSet.as_view({'get': 'history'})),
    path('v1/', include(router.urls)),

]
