from django.urls import  path, include
from rest_framework import routers
from .views import UserAppViewSet, ListUsers, ListGroups, MiProfileView, UserappFormChoicesList

from django.views.decorators.cache import cache_page
from django.conf import settings

router = routers.DefaultRouter()
router.register(r'userapp', UserAppViewSet, 'userapp')

urlpatterns = [
    path('v1/userapp/choices/', UserappFormChoicesList.as_view(), name="userapp-form-choices"),
    path('v1/userapp/myprofile/', MiProfileView.as_view({'get': 'get'})),
    path('v1/get_users_os/', ListUsers.as_view({'get': 'get_oraculo_user'})),
    path('v1/get_all_users/', ListUsers.as_view({'get': 'get_all_users'})),
    path('v1/groups/', ListGroups.as_view({'get': 'get_groups'})),
    path('v1/', include(router.urls)),
]