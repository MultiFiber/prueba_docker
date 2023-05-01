from .base import *  # noqa
from os.path import dirname, join

INSTALLED_APPS.insert(0,'grappelli')
INSTALLED_APPS.append('drf_yasg')
STATIC_ROOT = "/home/brujula_user/brujula_backend/brujula/static/"
MEDIA_URL = '/media/'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.AllowAny'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.TokenAuthentication'
    ]
}

TEMPLATES[0]['OPTIONS']['libraries'] = {'staticfiles':'django.templatetags.static'}
ROOT_URLCONF = 'config.urls_admin'
