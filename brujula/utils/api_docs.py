from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.views import APIView
from .views import get_user_by_token

from dotenv import load_dotenv
import os

schema_view = get_schema_view(
   openapi.Info(
      title= 'Brújula API',
      default_version='v1',
      description='Backend de Brújula',
      terms_of_service='https://www.multifiber.app/terminos_condiciones',
      contact=openapi.Contact(email='developers@multifiber.cl'),
      license=openapi.License(name='Licencia privada'),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


class GetMeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        request.user = get_user_by_token(request)
        return Response({
        request.user.name})