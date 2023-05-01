from rest_framework.authtoken.models import Token
import pytest
from rest_framework.test import force_authenticate
from tecnico.models import Disponibility
from ..models import Os, Displacement, OperatorPlans, Client
from datetime import datetime
from ostype.models import Ostype
from category.models import Category
from operador.models import Operator
from tecnico.models import Technician
from direction.models import Direction
from userapp.models import UserApp
from django.contrib.auth.models import User
from rest_framework.test import APIClient
import random
import datetime as date

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
        name="Calle Test 1",
        dirtype=0,
        deleted=False,
        iso = 've'
    )
    direction.save()
    return direction

@pytest.fixture
def direction_two():

    direction = Direction(
        name="Calle Test 2",
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
def disponibility_one(direction_one):
    disponibility = Disponibility(
        schedule_status = 0,
        schedule_day = 0,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('17:00', '%H:%M'),
        hours_unassigned = datetime.strptime('08:00', '%H:%M')
        )
    disponibility.save()
    return disponibility

@pytest.fixture
def disponibility_two(direction_one, disponibility_one):
    disponibility = Disponibility(
        schedule_status = 0,
        schedule_day = 0,
        dir = direction_one,
        schedule_start_time = datetime.strptime('08:00', '%H:%M'),
        schedule_end_time = datetime.strptime('09:00', '%H:%M'),
        father = disponibility_one,
        hours_unassigned = datetime.strptime('01:00', '%H:%M')
        )
    disponibility.save()
    return disponibility

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
def OS_one(technician_one, os_type_one, category_one, operator_one, disponibility_two, operator_plans_one, client_one):

    os = Os(
        status =  0,
        technician = technician_one,
        ostype = os_type_one,
        category = category_one,
        technology = 'technology',
        operator = operator_one,
        disponibility_hours = disponibility_two,
        plan_brujula = operator_plans_one,
        user_brujula = client_one,
        user_id = 1,
        plan_id = operator_plans_one.ID,
    )
    os.save()
    return os

@pytest.fixture
def displacement_one(direction_one, direction_two, OS_one):

    time = '02:00:00'
    displacement = Displacement(
        date = date.datetime.now(),
        direction_init = direction_one,
        direction_final = direction_two,
        km_init = 2,
        km_final = 16,
        os = OS_one,
        medio_desplazamiento = 0,
        displacement_time = datetime.strptime(time, '%H:%M:%S'),
        sequential_id = 1
    )
    displacement.save()
    return displacement

@pytest.mark.django_db
def test_create_displacement(user_one, token_one, displacement_one, direction_one, direction_two, OS_one):  

    user = UserApp.objects.get(email=user_one.email)
    client.force_authenticate(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token_one.key)

    payload = {
        'date': displacement_one.date, 
        'direction_init' : direction_one.pk,
        'direction_final' : direction_two.pk,
        'km_init' : 23,
        'km_final' : 45,
        'os' : OS_one.pk,
        'medio_desplazamiento' : 0,
        'displacement_time' : '01:00:00'
    }
    
    response = client.post('/api/v1/displacement/', payload , format='json')
    assert  response.status_code == 201


@pytest.mark.django_db
def test_delete_displacement(displacement_one):

    response = client.delete(f'/api/v1/displacement/{displacement_one.pk}/')
    assert  response.status_code == 204


@pytest.mark.django_db
def test_get_displacement():

    displacement = Displacement.objects.all()
    response = client.get('/api/v1/displacement/')
    assert  len(response.data) == len(displacement)

   

