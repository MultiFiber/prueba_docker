import os
import django
import pytest
from PIL import Image
from userapp.models import UserApp
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
from ostype.models import Ostype
from category.models import Category
from operador.models import Operator
from tecnico.models import Technician, Disponibility
from direction.models import Direction
from userapp.models import UserApp

client  = APIClient()

@pytest.fixture
def my_user(django_user_model):
    user: User = django_user_model(
        email = "user@example.com",
        password = "password",
        is_superuser = True
    )
    user.save()
    return user

@pytest.fixture
def my_token(my_user):
    token = Token(
        user = my_user
    )
    token.save()
    return token

@pytest.mark.django_db
def test_create_datatable(my_user, my_token):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + my_token.key)

    response = client.post('/api/v1/category/datatables/')
    assert  response.status_code == 200

@pytest.mark.django_db
def test_get_datatable():

    response = client.get('/api/v1/category/datatables_struct/')
    assert  response.status_code == 200