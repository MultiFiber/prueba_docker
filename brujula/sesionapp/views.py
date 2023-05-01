from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializer import HistorySessionSerializer
from .models import HistorySession
from utils.views import BaseViewSet
import timeago, datetime
from dateutil import parser
from .datatables import SesionDatatables
from django.http import JsonResponse
from rest_framework.decorators import action


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@method_decorator(cache_page(60*60*24), name = 'dispatch')
class SessionViewSet(BaseViewSet):

    queryset = HistorySession.objects.all()
    
    @method_decorator(cache_page(60*60*24), name = 'historysession')
    def historysession(self, request):
      
        serializer = HistorySessionSerializer(HistorySession.objects.filter(user=1), many=True)
        now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)
        historys = []
        for history in serializer.data:
            dt = parser.parse(history['date'])
            history['active'] = timeago.format(dt.replace(tzinfo  = None), now, 'es' )
            historys.append(history)

        return Response(historys)

    @method_decorator(cache_page(60*60*24), name = 'datatables_struct')
    @action(detail=False, methods=['get'])
    def datatables_struct(self, request) -> JsonResponse:
        return JsonResponse(SesionDatatables(request).get_struct(), safe=True)

    @method_decorator(cache_page(60*60*24), name = 'datatables')
    @action(detail=False, methods=['post'])
    def datatables(self, request) -> JsonResponse:
        return SesionDatatables(request).get_data()
    

