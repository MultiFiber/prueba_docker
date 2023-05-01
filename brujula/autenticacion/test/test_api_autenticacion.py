import os
import django
import pytest
from userapp.models import UserApp
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


client  = APIClient()
version = 'v1'

@pytest.fixture
def my_user():
    user = UserApp (
        name = "Ale",
        last_name= "Gonzalez",
        phone = "4242098193",
        email = "arreman@example.com",
        password = "11115667"
    )
    user.save()
    return user

@pytest.mark.django_db
def test_signup(my_user):
    payload = {
        'name' : 'Aguacate',
        'last_name' : 'Verde',
        'phone' : '987654321',
        'email' : 'user@example.com',
        'password' : '1234',
    }
    #VALIDANDO TOKEN DE AUTENTICACION

    response = client.post(f'/api/{version}/signup', payload, format="json") 

    assert  'token' in response.data
    
    #VALIDANDO QUE EL USUARIO FUE REGISTRADO
    exist = UserApp.objects.filter(email=my_user.email).exists()
    assert exist

    #VALIDANDO QUE EL TOKEN DE SESION FUE REGISTRADO
    token = Token.objects.filter(key=response.data['token']).first()
    assert token
    
@pytest.mark.django_db
def test_singin(my_user):
    payload = {
        'email' : my_user.email,
        'password' : my_user.password,
    }
    
    response = client.post(f'/api/{version}/signin', payload, format="json")  
    assert  response.status_code == 200

@pytest.mark.django_db
def test_signout():
    
    response = client.get(f'/api/{version}/signout')
    assert  response.status_code == 200