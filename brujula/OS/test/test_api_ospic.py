import os
import django
import pytest
from rest_framework.test import force_authenticate
from ..models import Os, OsPic
from ostype.models import Ostype
from category.models import Category
from operador.models import Operator
from tecnico.models import Technician, Disponibility
from direction.models import Direction
from userapp.models import UserApp
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import random
import tempfile

client = APIClient()
id_ospic = 0

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
    operator = Operator(
        name="name",
        code=1234,
        country=my_dir,
    )

    operator.save()
    return operator


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

@pytest.fixture
def my_disponibility(my_dir):
    disponibility = Disponibility(
        schedule_status = 0,
        schedule_day = 1,
        dir = my_dir,
        schedule_start_time = '9:00',
        schedule_end_time = '14:00',
    )
    disponibility.save()
    return disponibility

@pytest.fixture
def my_OS(my_user, my_ostype, my_category, my_technician, my_operator, my_disponibility):

    os = Os(
        status=0,
        technician=my_technician,
        ostype=my_ostype,
        category=my_category,
        technology="technology",
        operator=my_operator,
        plan="Testing",
        user_id= 1,
        disponibility = my_disponibility,
    )
    os.save()
    return os
    
@pytest.fixture
def my_ospic(my_OS):

    ospic = OsPic(
        owner_os=my_OS,
        photo="photo",
        caption="caption",
        
    )

    print(my_OS)
    ospic.save()
    return ospic


@pytest.mark.django_db
def test_create_ospic(my_user, my_OS):

    client.force_authenticate(user=my_user)

    image = Image.new('RGB', (100, 100))

    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file)
    tmp_file.seek(0)

    payload = {
        'photo': tmp_file,
        'caption': 'caption',
        'owner_os': my_OS.pk,
    }

    response = client.post('/api/v1/ospic/', payload, format='multipart')
    assert response.status_code == 201


@pytest.mark.django_db
def test_delete_ospic(my_ospic):

    response = client.delete(f'/api/v1/ospic/{my_ospic.pk}/')
    assert response.status_code == 204

# reverse_lazy('os')

@pytest.mark.django_db
def test_get_ospic():

    ospic = OsPic.objects.all()
    response = client.get('/api/v1/ospic/')
    
    assert len(response.data) == len(ospic)
