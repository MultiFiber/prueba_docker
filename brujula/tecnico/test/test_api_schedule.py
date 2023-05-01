import os
import django
import pytest
from rest_framework.test import force_authenticate
from tecnico.models import Technician, TechnicianPic, Disponibility, Schedule, Absence
from direction.models import Direction
from operador.models import Operator
from userapp.models import UserApp
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.forms.models import model_to_dict
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
def operate(my_dir):

    operador = Operator(
        name='Operador1',
        code=123456,
        country=my_dir,
    )
    operador.save()
    return operador


@pytest.fixture
def technician(operate, my_user):

    technician = Technician(
        birthday='2012-12-12',
        id_type=0,
        id_number='123456789',
        name='name',
        last_name='last_name',
        operator=operate,
        status=0,
        user_id = my_user.id,
        device_options = 0,
        device_version = 0,
    )
    technician.save()
    return technician


@pytest.fixture
def my_disponibility(my_dir):
    disponibility = Disponibility(
        schedule_day=0,
        schedule_status=0,
        dir=my_dir,
        schedule_start_time='9:00',
        schedule_end_time='12:00'

    )

    disponibility.save()
    return disponibility


@pytest.fixture
def my_absence(operate):
    absence = Absence(
        operator=operate,
        status=0,
        schedule_day=0,
        start_time='9:00',
        end_time='15:00'

    )
    absence.save()
    return absence


@pytest.fixture
def my_schedule(technician, my_disponibility, my_absence):
    schedule = Schedule(
        schedule_start_date='2012-12-12 8:00',
        schedule_end_date='2012-12-12 15:00',
        technician=technician
    )
    schedule.save()
    schedule.absence.add(my_absence)
    schedule.disponibility.add(my_disponibility)
    return schedule


@pytest.mark.django_db
def test_create_schedule(my_user, technician, my_absence, my_disponibility):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    payload = {
        'schedule_start_date': '2012-12-12 8:00',
        'schedule_end_date': '2012-12-12 15:00',
        'technician': technician.pk,
        'disponibility': [my_disponibility.pk],
        'absence': [my_absence.pk],
    }

    response = client.post('/api/v1/schedule/', payload, format='json')
    print(response.data)
    assert response.status_code == 201


@pytest.mark.django_db
def test_delete_schedule(my_schedule):

    response = client.delete(f'/api/v1/schedule/{my_schedule.pk}/')
    assert response.status_code == 204

# reverse_lazy('os')
