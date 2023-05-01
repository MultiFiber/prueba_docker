from .models import Ostype
from .serializer import OstypeSerializer
from .datatables import OstypeDatatable
from django.http import JsonResponse
from rest_framework.decorators import action
from utils.views import BaseViewSet


class OstypeViewSet(BaseViewSet):
    serializer_class = OstypeSerializer   
    queryset = Ostype.objects.all()
    filter_fields = ["ID", "operator", "name", "color"]

    def get_queryset(self):
        user = self.request.user 

        if user.is_superuser:
            o = self.request.query_params.get('operator')
            if o:
                return Ostype.objects.filter(operator__ID=o)
            return Ostype.objects.all()

        return Ostype.objects.filter(operator=user.operator)
        
    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(OstypeDatatable(request).get_struct(), safe=True)

    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return OstypeDatatable(request).get_data()
    
