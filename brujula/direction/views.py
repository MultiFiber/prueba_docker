from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from utils.views import BaseViewSet, MultipleChoicesAPIView
from utils.permissions import OnlyView

from .serializers import DirectionSerializers, DirectionSearchSerializers
from .models import Direction, dir_type, building_type


def show_directions(request, id):
    return render(request, "directions.html", {'directions': Direction.objects.all()})


class DirectionView(BaseViewSet):
    serializer_class = DirectionSerializers
    queryset = Direction.objects.all()
    filterset_fields = ["name","dirtype","buildingtype","parent"]
    #*No se puede filtrar por ID's debido a la clase Meta, queda pendiente revisar

    @action(detail=True, methods=['get'])
    def get_descendants(self, request, pk):
        qs = Direction.objects.filter(id=pk).prefetch_related('children')
        qs = qs.get_descendants(include_self=True)
        return Response(DirectionSerializers(qs, many=True).data)

    @action(detail=False, methods=['get'])
    def search(self, request, **kwargs):
        from django.contrib.postgres.search import SearchVector
        from django.contrib.postgres.search import SearchQuery
        from django.contrib.postgres.search import SearchRank
        from django.db.models import Q
        _q = request.query_params.get('generic','')
        qs = Direction.objects.none()

        #Busqueda simple
        mi_search = Direction.objects.filter(Q(name__unaccent__icontains=_q) | Q(full_direction__icontains=_q))
        if mi_search.all().count() > 0:
            qs = mi_search.all()


        #Busqueda por vector
        mi_search = Direction.objects.annotate(
                    search=SearchVector('name', 'full_direction'))\
                    .filter(search=_q)
        if mi_search.all().count() > 0:
            qs = mi_search.all()


        mi_search = Direction.objects.annotate(
                    search=SearchVector('name', 'full_direction'))\
                    .filter(search__icontains=_q)
        if mi_search.all().count() > 0:
            qs = mi_search.all()


        # new_search = Direction.objects.annotate(
        #             search=SearchVector('name', 'full_direction'))\
        #             .filter(search__icontains=SearchQuery(_q))
        # qs = new_search.all()

        return Response(DirectionSearchSerializers(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def retrive_or_create(self, request, **kwargs):
        import json
        from .models import GoogleGeocodeLatlng
        data_in = json.loads(request.body)
        if 'OK' == data_in['status']:
            try:
                GoogleGeocodeLatlng.objects.get(name=data_in['results'][1]['formatted_address'])
            except Exception as e:
                GoogleGeocodeLatlng.objects.create(result=data_in, name=data_in['results'][1]['formatted_address'])
            return Response({'brujula_id':1})
        else:
            return Response({'brujula_id':0})
        



class DirectionFormChoicesList(MultipleChoicesAPIView):
    """
    List all choices for users dir_type, building_type
    """
    choices_response = {"dir_type": dir_type,
                        "building_type": building_type,}



class ChoicesByCountry(APIView):
    operator_param = openapi.Parameter('country', openapi.IN_QUERY, 
    description="Operador para hacer la busqueda",
    type=openapi.TYPE_STRING)

    def reformat_object(self, array):
        return [{"ID": obj[0], "name": obj[1]} for obj in array]

    @swagger_auto_schema(manual_parameters=[operator_param])
    def get(self, request, **kwargs):
        
        country = request.GET.get('country')
        c = Direction.objects.get(id=country)

        all_documents = {
            "CL": (
                (0, 'pasaporte'),
                (1, 'run'),
                (2, 'rut'),
            ),
            "VE": (
                (3, 'cedula'),
                (4, 'pasaporte')
            ),
            "PE": (
               (5, 'dni'),
               (6, 'ce')
            ),
         }

        return Response({
            "data":self.reformat_object(all_documents[c.iso.upper()]),
            "iso":c.iso.upper()
        })