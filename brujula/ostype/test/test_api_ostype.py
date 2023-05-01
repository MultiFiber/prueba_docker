import re
from unicodedata import name
import pytest
import os
import django
if 'env setting':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()
from ostype.models import Ostype
from operador.models import Operator
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate
from direction.models import Direction
from userapp.models import UserApp


client  = APIClient()

@pytest.fixture
def my_user(django_user_model):
    user: User = django_user_model(
        email="user@example.com",
        password="password",
    )

    user.save()

    return user

@pytest.fixture
def my_dir():
    direction = Direction(
        name="Calle",
        dirtype=0,
        deleted = False,
    )

    direction.save()

    return direction


@pytest.fixture
def operate(my_dir):

    operador = Operator(
        name = 'Operador',
        code = 123456,
        country = my_dir,
    )
    operador.save()
    return operador

@pytest.fixture
def my_ostype(operate):
    ostype = Ostype(
        operator = operate,
        name = 'OStype',
        color = 'rgb(255,86,48)'
    )

    ostype.save()
    return ostype

@pytest.mark.django_db
def test_create_ostype(my_user, my_ostype):
    
    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload =  {
        'operator' : my_ostype.operator.pk,
        'name' : my_ostype.name,
        'color' : my_ostype.color,
    }

    response = client.post('/api/v1/ostype/', payload, format='json')
    assert  response.status_code == 201

@pytest.mark.django_db
def test_get_ostype():

    ostype = Ostype.objects.all()
    response = client.get('/api/v1/ostype/')

    assert  len(response.data) == len(ostype)

@pytest.mark.django_db
def test_delete_ostype(my_ostype):

    response = client.delete(f'/api/v1/ostype/{my_ostype.pk}/')
    assert  response.status_code == 204

    
    
   


