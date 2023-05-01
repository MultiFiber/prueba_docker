import os
import django
import pytest
from rest_framework.test import force_authenticate
from tecnico.models import Technician, TechnicianPic, Disponibility
from direction.models import Direction
from userapp.models import UserApp
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import random
import tempfile

client = APIClient()


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
def my_disponibility(my_dir):
    disponibility = Disponibility(
        schedule_day = 0,
        schedule_status = 0,
        dir = my_dir,
        schedule_start_time = '9:00',
        schedule_end_time = '12:00'

    )

    disponibility.save()
    return disponibility

@pytest.mark.django_db
def test_create_disponibility(my_user, my_dir):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'schedule_day': 1,
        'schedule_status': 3,
        'dir' : my_dir.pk,
        'schedule_start_time' : '9:00',
        'schedule_end_time' : '12:00',
    }

    response = client.post('/api/v1/disponibility/', payload, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_delete_disponibility(my_disponibility):

    response = client.delete(f'/api/v1/disponibility/{my_disponibility.pk}/')
    assert response.status_code == 204

# reverse_lazy('os')


@pytest.mark.django_db
def test_get_disponibility():

    disponibility = Disponibility.objects.all()
    response = client.get('/api/v1/disponibility/')
    
    assert len(response.data) == len(disponibility) 
