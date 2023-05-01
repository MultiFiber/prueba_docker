
import os
import django
if 'env setting':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()
from operador.models import Operator
from direction.models import Direction
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.test import force_authenticate
from userapp.models import UserApp

client  = APIClient()

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
        name="Direction 1",
        dirtype=0,
    )

    direction.save()
    return direction

@pytest.fixture
def my_operator(my_dir):
    operator  = Operator(
        name="name",
        code=1234,
        country=my_dir,
    )

    operator.save()
    return operator

@pytest.mark.django_db
def test_create_operador(my_user,my_dir):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'name' : 'name',
        'code' : 1234,
        'country' : my_dir.pk,
    }
    
    response = client.post('/api/v1/operator/', payload , format='json')
    assert  response.status_code == 201

@pytest.mark.django_db
def test_delete_operador(my_operator):

    response = client.delete(f'/api/v1/operator/{my_operator.pk}/')
    assert  response.status_code == 204


@pytest.mark.django_db
def test_get_direction():

    operador = Operator.objects.all()
    response = client.get('/api/v1/operator/')
    assert  len(response.data) == len(operador)

