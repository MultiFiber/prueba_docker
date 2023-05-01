from utils.views import BaseViewSet
from .serializers import OperatorSerializers
from .models import Operator


class OperatorViewSet(BaseViewSet):
    serializer_class = OperatorSerializers
    queryset = Operator.objects.filter(deleted=False)
    filterset_fields = ['ID', "name", "operator_code", "country"]