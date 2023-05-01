import os
import django
import pytest
from userapp.models import UserApp
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from userapp.models import UserApp


client  = APIClient()
urls_post = [
    '/api/v1/os/datatables/',
    '/api/v1/ostype/datatables/',
    '/api/v1/category/datatables/',
    '/api/v1/displacement/datatables/',
    '/api/v1/userapp/datatables/',

]
urls_get = [
    '/api/v1/displacement/datatables_struct/',
    '/api/v1/os/datatables_struct/',
    '/api/v1/ostype/datatables_struct/',
    '/api/v1/category/datatables_struct/',
    '/api/v1/userapp/datatables_struct/',
]

@pytest.fixture
def my_user(django_user_model):
    user: User = django_user_model(
        email = "user@example.com",
        password = "password",
        is_superuser = True
    )
    user.save()
    return user

@pytest.fixture
def my_token(my_user):
    token = Token(
        user = my_user
    )
    token.save()
    return token

@pytest.mark.django_db
def test_create_datatable(my_user, my_token):

    user = UserApp.objects.get(email=my_user.email)
    client.force_authenticate(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + my_token.key)

    for item in urls_post:
        response = client.post(item)
        assert  response.status_code == 200

@pytest.mark.django_db
def test_get_datatable():
    for item in urls_get:
        response = client.get(item)
        assert  response.status_code == 200

