import os
import django
import pytest
from rest_framework.test import force_authenticate
from ostype.models import Ostype
from category.models import Category
from operador.models import Operator
from tecnico.models import Technician, TechnicianPic
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
    operator = Operator(
        name="name",
        code=1234,
        country=my_dir,
    )

    operator.save()
    return operator


@pytest.fixture
def my_technician(my_operator,my_user):
    tecnico = Technician(
        birthday="2012-12-12",
        id_type="0",
        id_number=123456789,
        name="Tecnico1",
        last_name="Tecnico1",
        operator=my_operator,
        status=0,
        user_id = my_user.id,
        device_options = 0,
        device_version = 0,
    )
    tecnico.save()
    return tecnico




@pytest.fixture
def my_tecpic(my_technician):

    tecpic = TechnicianPic(
        photo="photo",
        caption="caption",
        owner_tech=my_technician,
    )
    tecpic.save()
    return tecpic


@pytest.mark.django_db
def test_create_tecpic(my_user, my_technician):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)

    image = Image.new('RGB', (100, 100))

    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file)
    tmp_file.seek(0)

    payload = {
        'photo': tmp_file,
        'caption': 'caption',
        'owner_tech': my_technician.pk,
    }

    response = client.post('/api/v1/technicianpic/', payload, format='multipart')
    assert response.status_code == 201


@pytest.mark.django_db
def test_delete_tecpic(my_tecpic):

    response = client.delete(f'/api/v1/technicianpic/{my_tecpic.pk}/')
    assert response.status_code == 204

# reverse_lazy('os')


@pytest.mark.django_db
def test_get_tecpic():

    tecpic = TechnicianPic.objects.all()
    response = client.get('/api/v1/technicianpic/')
    
    assert len(response.data) == len(tecpic) 
