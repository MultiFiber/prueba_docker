import os
import django
import json
import pytest
from django.http import JsonResponse
from django.core import exceptions
import pytest
from datetime import datetime
from userapp.models import UserApp
from ..models import Os, status as status_os, Client, OperatorPlans
from operador.models import Operator
from direction.models import Direction
from ostype.models import Ostype
from category.models import Category
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from tecnico.models import Technician, Disponibility
from django.contrib.auth.models import User
from userapp.models import UserApp


client  = APIClient()

@pytest.fixture
def user_one(django_user_model):
    user: User = django_user_model(
        email = "user@example.com",
        password = "password",
        is_superuser = True
    )
    user.save()
    return user

@pytest.fixture
def token_one(user_one):
    token = Token(
        user = user_one
    )
    token.save()
    return token

@pytest.fixture
def direction_one():

    direction = Direction(
        name="Calle Test",
        dirtype=0,
        deleted=False,
        iso = 've'
    )
    direction.save()
    return direction

@pytest.fixture
def operator_one(direction_one):

    operador = Operator(
        name='Operador Test',
        operator_code=123456,
        country=direction_one,
        email='operator.one@example.com'
    )
    operador.save()
    return operador

@pytest.fixture
def os_type_one(operator_one, ):
    os_type = Ostype(
        operator = operator_one,
        name = 'OS Type Test', 
        color = '#000000',
        tag = 'Negro',
        sequential_id = 1,
        )
    os_type.save()
    return os_type

@pytest.fixture
def category_one(os_type_one):
    category = Category(
        name = 'Category Test',
        duration = 60,
        imgs =  {
                    'one': 'image'
                },
        questions = {
                        'one': 'question'
                    },
        os_type = os_type_one,
        sequential_id = 1
        )
    category.save()
    return category

@pytest.fixture
def technician_one(operator_one, user_one):
    tecnico = Technician(
        birthday = "2000-12-12",
        id_type = 0,
        id_number = 123456789,
        name = "Nombre Test",
        last_name = "Apellido Test",
        operator = operator_one,
        status = 0,
        user = user_one,
        device = {
                    "one": 0,
                },
        is_supervisor = False,
        sequential_id = 1
    )
    tecnico.save()
    return tecnico

@pytest.fixture
def disponibility_one(direction_one):
    disponibility = Disponibility(
        schedule_status = 0,
        schedule_day = 0,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('17:00', '%H:%M'),
        )
    disponibility.save()
    return disponibility

@pytest.fixture
def client_one(operator_one, direction_one):
    client = Client(
        first_name = 'name',
        last_name = 'last name',
        document_type = 0,
        document_number = '12839243',
        phone = '92373838',
        service_number = 1,
        direction = direction_one,
        direction_text = 'text example one',
        operator = operator_one
    )
    client.save()
    return client

@pytest.fixture
def operator_plans_one(operator_one):
    operator = OperatorPlans(
        operator = operator_one,
        tradename = 'name operator',
        technology = 'technology name'
    )
    operator.save()
    return operator

@pytest.fixture
def disponibility_two(direction_one, disponibility_one):
    disponibility = Disponibility(
        schedule_status = 0,
        schedule_day = 0,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('09:00', '%H:%M'),
        father = disponibility_one
        )
    disponibility.save()
    return disponibility

@pytest.mark.django_db
def request_client(ID, payload):
    response = client.put(f'/api/v1/os/{ID}/', payload, format="json")
    return response

@pytest.mark.django_db
def test_status_changes(technician_one,user_one, token_one, operator_one, category_one, os_type_one, disponibility_one, direction_one, client_one, operator_plans_one):

    user = UserApp.objects.get(email=user_one.email)
    client.force_authenticate(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_one.key)
    
    for data in status_os:
        
        for item in status_os:
            payload_d = {
                            'schedule_status' : 0,
                            'schedule_day' : 0,
                            'dir' : direction_one.pk,
                            'schedule_start_time' : '08:00',
                            'schedule_end_time' :'09:00',
                            'father' : disponibility_one.pk
                        }
            response_d = client.post('/api/v1/disponibility/', payload_d, format='json')
            disponibility = response_d.json()
            payload_o = {
                            'status': data[0],
                            'technician': technician_one.pk,
                            'ostype': os_type_one.pk,
                            'category': category_one.pk,
                            'technology': 'technology',
                            'operator': operator_one.pk,
                            'disponibility_hours' : disponibility['ID'],
                            'plan_brujula': operator_plans_one.pk,
                            'user_brujula' : client_one.pk,
                            'user_id': 1,
                            'plan_id': operator_plans_one.pk
                        }
            
            response_o = client.post('/api/v1/os/', payload_o, format='json')
            payload_o["status"] = item[0]
            os = response_o.json()
        
            try:
                response_b = request_client(os['ID'], payload_o)
                status_code = response_b.status_code
            except exceptions.ValidationError:
                status_code = 400

            if data[0] == 0:
                if (
                            item[0] == 5 or 
                            item[0] == 6 or
                            item[0] == 7 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 0 or 
                            item[0] == 1 or 
                            item[0] == 2 or 
                            item[0] == 3 or
                            item[0] == 4 
                        ):
                    assert status_code == 200 
            elif data[0] == 1:
                if (
                            item[0] == 0 or 
                            item[0] == 5 or 
                            item[0] == 6 or
                            item[0] == 7 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 2 or 
                            item[0] == 3 or
                            item[0] == 1 or 
                            item[0] == 4 
                        ):
                    assert status_code == 200
            elif data[0] == 2:
                if (
                            item[0] == 0 or
                            item[0] == 1 or
                            item[0] == 5 or 
                            item[0] == 4 or
                            item[0] == 7 
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 6 or
                            item[0] == 2 or  
                            item[0] == 8 or 
                            item[0] == 3 
                        ):
                    assert status_code == 200
            elif data[0] == 3:
                if (
                            item[0] == 0 or 
                            item[0] == 4 or
                            item[0] == 6 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif ( 
                            item[0] == 2 or 
                            item[0] == 3 or
                            item[0] == 1 or 
                            item[0] == 5 or
                            item[0] == 7 
                        ):
                    assert status_code == 200
            elif data[0] == 4:
                if (
                            item[0] == 0 or 
                            item[0] == 1 or 
                            item[0] == 5 or
                            item[0] == 6 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 2 or 
                            item[0] == 3 or
                            item[0] == 4 or 
                            item[0] == 7
                        ):
                    assert status_code == 200
            elif data[0] == 5:
                if (
                            item[0] == 0 or 
                            item[0] == 1 or
                            item[0] == 2 or
                            item[0] == 3 or
                            item[0] == 4 or 
                            item[0] == 6 or
                            item[0] == 7 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 5 
                        ):
                    assert status_code == 200
            elif data[0] == 6:
                if (
                            item[0] == 0 or 
                            item[0] == 1 or
                            item[0] == 2 or
                            item[0] == 3 or
                            item[0] == 4 or 
                            item[0] == 5 or
                            item[0] == 7 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 6 
                        ):
                    assert status_code == 200
            elif data[0] == 7:
                if (
                            item[0] == 6 or 
                            item[0] == 1 or
                            item[0] == 2 or
                            item[0] == 3 or
                            item[0] == 4 or 
                            item[0] == 5 or
                            item[0] == 8
                        ):
                    assert status_code == 400
                elif(
                            item[0] == 0 or
                            item[0] == 7  
                        ):
                    assert status_code == 200
            elif data[0] == 8:
                if (
                            item[0] == 0 or 
                            item[0] == 1 or
                            item[0] == 2 or
                            item[0] == 3 or
                            item[0] == 4 or 
                            item[0] == 5 or
                            item[0] == 7 or
                            item[0] == 6
                        ):
                    assert status_code == 400
                elif (
                            item[0] == 8
                        ):
                    assert status_code == 200

            