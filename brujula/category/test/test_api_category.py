import os
import django
if 'env setting':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    django.setup()
import pytest
from ostype.models import Ostype
from category.models import Category
from operador.models import Operator
from direction.models import Direction
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from userapp.models import UserApp
from rest_framework.test import force_authenticate
import random

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

@pytest.fixture
def my_ostype(my_operator):
    ostype = Ostype(
        operator=my_operator,
        name="name",
        color="color",
    )
    ostype.save()
    return ostype

@pytest.fixture
def my_category(my_ostype):
    category = Category(
        name="name",
        duration=0,
        imgs="imgs",
        questions="questions",
        os_type=my_ostype,
        description="description",
    )

    category.save()
    return category


@pytest.mark.django_db
def test_create_category(my_user,my_category):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'name' : my_category.name,
        'duration': my_category.duration,
        'imgs': my_category.imgs,
        'questions': my_category.questions,
        'os_type': my_category.os_type.pk,
        'description' : my_category.description,
    }
    
    response = client.post('/api/v1/category/', payload , format='json')
    print(response.json())
    assert  response.status_code == 201
    #assert  payload['status'] == response.data['status']
    #assert  payload['technician'] == response.data['technician']
    #assert  payload['plan'] == response.data['plan']

@pytest.mark.django_db
def test_delete_category(my_category):

    response = client.delete(f'/api/v1/category/{my_category.pk}/')
    assert  response.status_code == 204

#reverse_lazy('os')


@pytest.mark.django_db
def test_get_category():

    category = Category.objects.all()
    response = client.get('/api/v1/category/')
    assert  len(response.data) == len(category)
    
    
   

