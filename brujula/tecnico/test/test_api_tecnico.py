from email import header
from urllib import response
from wsgiref import headers
import pytest
import os
import django
from rest_framework.test import force_authenticate
if 'env setting':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()
from ..models import Technician
from operador.models import Operator
from django.contrib.auth.models import User
from userapp.models import UserApp
from rest_framework.test import APIClient
from direction.models import Direction
import json

client = APIClient()


@pytest.fixture
def my_user(django_user_model):
    user: User = django_user_model(
        email="user@gmail.com",
        password="password",
    )
    user.save()

    return user


@pytest.fixture
def my_dir():
    direction = Direction(
        name="Calle",
        dirtype=0,
        deleted=False,
    )
    direction.save()

    return direction


@pytest.fixture
def my_operator(my_dir):

    operador = Operator(
        name='Operador1',
        code=123456,
        country=my_dir,
    )
    operador.save()
    return operador


@pytest.fixture
def my_technician(my_operator, my_user):
    tecnico = Technician(
        birthday="2012-12-12",
        id_type="0",
        id_number=123456789,
        name="Tecnico1",
        last_name="Tecnico1",
        operator=my_operator,
        status = 0,
        user_id = my_user.id,
        device_options = 0,
        device_version = 0,
    )
    tecnico.save()
    return tecnico


@pytest.mark.django_db
def test_technician_create(my_user, my_operator):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'birthday': '2012-12-12',
        'id_type': 0,
        'id_number': '123457789',
        'name': 'name',
        'last_name': 'last_name',
        'operator': my_operator.pk,
        'status': 0,
        'user_id' : my_user.pk,
        'device_options' : 0,
        'device_version' : 0,
    }

    reponse = client.post('/api/v1/technician/', payload, format='json')
    assert reponse.status_code == 201
    #assert payload['tecnico'] == reponse.data['tecnico']


@pytest.mark.django_db
def test_delete_tecnico(my_technician):

    response = client.delete(f'/api/v1/technician/{my_technician.pk}/')
    assert response.status_code == 204


@pytest.mark.django_db
def test_get_tecnico():

    tecnico = Technician.objects.all()
    response = client.get('/api/v1/technician/')
    assert len(response.data) == len(tecnico)
