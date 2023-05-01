
import os
import django
if 'env setting':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()
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

@pytest.mark.django_db
def test_create_direction(my_user):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'name' : 'Direction 1',
        'dirtype' : 0,
    }
    
    response = client.post('/api/v1/direction/', payload , format='json')
    assert  response.status_code == 201

@pytest.mark.django_db
def test_delete_direction(my_dir):

    response = client.delete(f'/api/v1/direction/{my_dir.pk}/')
    assert  response.status_code == 204


@pytest.mark.django_db
def test_get_direction():

    direction = Direction.objects.all()
    response = client.get('/api/v1/direction/')
    assert  len(response.data) == len(direction)

