import os
import django
import pytest
from rest_framework.test import force_authenticate
from operador.models import Operator
from direction.models import Direction
from tecnico.models import Technician, TechnicianPic, Absence
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
def my_operator(my_dir):
    operator  = Operator(
        name="name",
        code=1234,
        country=my_dir,
    )

    operator.save()
    return operator

@pytest.fixture
def my_absence(my_operator):
    absence = Absence(
        operator=my_operator,
        schedule_day=0,
        status=0,
        start_time='9:00',
        end_time='15:00'

    )
    absence.save()
    return absence

@pytest.mark.django_db
def test_create_absence(my_user, my_absence):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'operator' : my_absence.operator.pk,
        'schedule_day':0,
        'status' : 0,
        'start_time' : '9:00',
        'end_time' : '15:00'
    }

    response = client.post('/api/v1/absence/', payload, format='json')
    assert response.status_code == 201


@pytest.mark.django_db
def test_delete_disponibility(my_absence):

    response = client.delete(f'/api/v1/absence/{my_absence.pk}/')
    assert response.status_code == 204

# reverse_lazy('os')


@pytest.mark.django_db
def test_get_disponibility(my_user):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    absence = Absence.objects.all()
    response = client.get('/api/v1/absence/')
    
    assert len(response.data) == len(absence) 
