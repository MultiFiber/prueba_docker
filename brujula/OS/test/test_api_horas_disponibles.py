import os
import django
import json
from django.http import JsonResponse
import pytest
from datetime import datetime, timedelta
from userapp.models import UserApp
from ..views import list_of_hours_method, list_of_technician_availables_method 
from operador.models import Operator
from direction.models import Direction
from ostype.models import Ostype
from category.models import Category
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from tecnico.models import Technician, Disponibility, Absence, Schedule, Holiday
from django.contrib.auth.models import User
from userapp.models import UserApp
from utils.exceptions import custom_exception_handler
from rest_framework.exceptions import ValidationError

client  = APIClient()

def to_seconds(hora):
    formato = "%H:%M:%S"
    hora = hora.strftime(formato)
    lista = hora.split(":")
    hh=int(lista[0])*3600
    mm=int(lista[1])*60
    ss=int(lista[2])
    suma = hh + mm + ss
    return suma

def to_hh_mm_ss(segundos):
    hor = (segundos / 3600)
    min = ((segundos - hor * 3600) / 60)
    seg = segundos - (hor * 3600 + min * 60) 
    if hor < 10:
        hor = f'0{int(hor)}'
    else:
        hor = f'{int(hor)}'
    if min < 10:
        min = f'0{int(min)}'
    else:
        min = f'{int(min)}'
    if seg < 10:
        seg = f'0{int(seg)}'
    else:
        seg = f'{int(seg)}'
    return f"{hor}:{min}:{seg}"

@pytest.fixture
def user_one(django_user_model):
    user: User = django_user_model(
        email = "user_test@example.com",
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
        schedule_day = 1,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('17:00', '%H:%M'),
        )
    disponibility.save()
    return disponibility

@pytest.fixture
def disponibility_two(direction_one):
    disponibility = Disponibility(
        schedule_status = 0,
        schedule_day = 3,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('13:00', '%H:%M')
        )
    disponibility.save()
    return disponibility

@pytest.fixture
def disponibility_three(direction_one, disponibility_two):
    disponibility = Disponibility(
        schedule_status = 1,
        schedule_day = 3,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('09:00', '%H:%M'),
        father = disponibility_two
        )
    disponibility.save()
    return disponibility

@pytest.fixture
def absence_one(operator_one):
    absence = Absence(
        sequential_id = 1,
        operator = operator_one,
        status = 1,
        time_start = datetime.strptime('2023-02-23 11:00', '%Y-%m-%d %H:%M'),
        time_end = datetime.strptime('2023-02-23 12:00', '%Y-%m-%d %H:%M'),
        type = 1
    )
    absence.save()
    return absence

@pytest.fixture
def absence_two(operator_one):
    absence = Absence(
        sequential_id = 2,
        operator = operator_one,
        status = 1,
        time_start = datetime.strptime('2023-02-27 13:00', '%Y-%m-%d %H:%M'),
        time_end = datetime.strptime('2023-02-27 14:00', '%Y-%m-%d %H:%M'),
        type = 1
    )
    absence.save()
    return absence

@pytest.fixture
def holiday_one(operator_one):
    holiday = Holiday(
        day = '2023-02-20',
        name = 'Carnavales',
        status = 0,
        holiday_type = 1,
        Operator = operator_one,
        sequential_id = 1,
    )
    holiday.save()
    return holiday

@pytest.fixture
def schedule_one(technician_one, disponibility_one, disponibility_two, absence_one, absence_two, holiday_one):
    schedule = Schedule(
        schedule_start_date='2023-02-20',
        schedule_end_date='2023-03-03',
        technician=technician_one,
    )
    schedule.save()
    schedule.absence.add(absence_one)
    schedule.absence.add(absence_two)
    schedule.disponibility.add(disponibility_one)
    schedule.disponibility.add(disponibility_two)
    schedule.Holiday.add(holiday_one)
    return schedule    

@pytest.mark.django_db
def test_day_validation_in_technical_hours(user_one, token_one, operator_one, schedule_one):

    user = UserApp.objects.get(email=user_one.email)
    client.force_authenticate(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_one.key)

    day = input('\n Ingrese un día en formato DD-MM-YYYY: ')
    data = list_of_technician_availables_method(operator_one,day)
    assert data != []
    print (f"\n Lista de Técnicos disponibles para la fecha = {day}: ", data)

@pytest.mark.django_db
def test_segmentation_of_available_hours_of_the_technician(technician_one,user_one, token_one, operator_one, schedule_one, category_one, absence_one, absence_two, disponibility_three):

    user = UserApp.objects.get(email=user_one.email)
    client.force_authenticate(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_one.key)

    now = datetime.now()
    day = input('\n Ingrese un día en formato DD-MM-YYYY: ')
    technician = [technician_one.ID, None]
    category = category_one.ID
    time = Category.objects.get(ID=int(category))
    schedule_technician_response = list_of_technician_availables_method(operator_one, day)
    seconds = int(time.duration) * 60

    day_format=datetime.strptime(day, '%d-%m-%Y')
    list_of_hour_range = []

    data = schedule_technician_response

    if len(schedule_technician_response) == 0:

        raise ValidationError({'message':'Objeto no encontrado'})

    if day_format > now:

        for t in technician:

            if t is not None: 

                filtr = {}
                filtr['names_technicians_available'] = list(filter(lambda item: item['id_technician'] == int(t), data))
                list_of_hour_range = list_of_hours_method(filtr['names_technicians_available'],seconds)

            else:

                list_of_hour_range = list_of_hours_method(data,seconds)

            if len(list_of_hour_range) < 1:

                raise ValidationError({'message':'Objeto no encontrado'})

            assert list_of_hour_range != []
            values = []
            for item in list_of_hour_range: 
                values.append(item['hours'])
                assert values.count(item['hours']) == 1
            print(f"\n ID Técnico = {t}: ",list_of_hour_range)

    else:

        raise ValidationError({'message':'Fecha incorrecta para agendar'})
            