from django.shortcuts import render
from .serializers import *
from .models import Category, ResponseOs
from utils.views import BaseViewSet
from .datatables import CategoryDatatable
from django.http import JsonResponse
from rest_framework.decorators import action
#from django.core.cache.backends.base import DEFAULT_TIMEOUT
import django_filters



class CategoryFilter(django_filters.FilterSet):
    #? filtro definitivo
    class Meta:
        model = Category
        exclude = ['imgs','questions']


class CategoryView(BaseViewSet):
    serializer_class = CategorySerializers
    queryset = Category.objects.all()
    filterset_fields = ['ID','duration','name','description','os_type']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Category.objects.all()
        # print(Category.objects.filter(os_type__operator=self.request.user.operator).count())
        return Category.objects.filter(os_type__operator=self.request.user.operator)

    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(CategoryDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return CategoryDatatable(request).get_data()


class ResponseOsViewV1(BaseViewSet):
    queryset = ResponseOs.objects.all().order_by('ID')
    filterset_fields = ['ID','ref_os']
    serializer_class = ResponseOsSerializersV1
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return ResponseOs.objects.all()
        return ResponseOs.objects.filter(ref_os__operator=self.request.user.operator)

class ResponseOsViewV2(ResponseOsViewV1):
    serializer_class = ResponseOsSerializersV2


    def get_queryset(self):
        if self.request.user.is_superuser:
            return ResponseOs.objects.all()
        return ResponseOs.objects.filter(ref_os__operator=self.request.user.operator)