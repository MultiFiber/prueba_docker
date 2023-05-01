from django.urls import path, include
from rest_framework import routers
from django.views.decorators.cache import cache_page
from . import views

router = routers.DefaultRouter()
router.register(r'direction', views.DirectionView, 'Direction')

urlpatterns = [    
    path('v1/directions/<int:id>', views.show_directions),
    path('v1/directions/choices/', views.DirectionFormChoicesList.as_view(), name="direction-form-choices"),
    path('v1/choices_by_country/', views.ChoicesByCountry.as_view(), name="choices-by-country"),
    path('v1/', include(router.urls)),
]
