"""
Django settings for marketplace project.

Generated by 'django-admin startproject' using Django 3.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from . import get_env_variable
import os

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

DATA_UPLOAD_MAX_MEMORY_SIZE = get_env_variable("DATA_UPLOAD_MAX_MEMORY_SIZE", 15242880)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SITE_NAME = 'brujula'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django_filters',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',    
    'rest_framework',
    'autenticacion',
    'category',
    'direction',
    'operador',
    'operator_setting',
    'OS',
    'ostype',
    'tecnico',
    'utils',
    'mptt',
    'userapp',
    'sesionapp',
    'django_rest_passwordreset',
    'django_celery_beat',
    'report',
]

DATE_INPUT_FORMATS = ['%d-%m-%Y']
DATE_FORMAT = "%d-%m-%Y"

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PERMISSION_CLASSES':[
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication'
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DATE_INPUT_FORMATS': DATE_INPUT_FORMATS,
    'DATE_FORMAT': DATE_FORMAT,
    'DATETIME_FORMAT': "%d-%m-%Y %H:%M:%S",
    #'DEFAULT_VERSIONING_CLASS': 'utils.versioning.AppVersioning',    
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'utils.pagination.DefaultResultsSetPagination',        
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",      
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # "django.middleware.locale.LocaleMiddleware",
    # "django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    # "config.middlewares.ActiveUserMiddleware",
    # 'corsheaders.middleware.CorsMiddleware',
]

__CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': get_env_variable('REDIS_CACHE_LOCATION', 'redis://127.0.0.1:6379'),
        'TIMEOUT': 60 * 60 * 24,
        'OPTIONS': {
            'db': get_env_variable('REDIS_CACHE_DB','16'),
            'parser_class': 'redis.connection.PythonParser',
            'pool_class': 'redis.BlockingConnectionPool',
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': f'unique-key-{SITE_NAME}',
    }
}

CACHES_TIMES = {
    "min":60,
    "max":60*60
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {

    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": get_env_variable("DB_NAME"),
        "USER": get_env_variable("DB_USER"),
        "PASSWORD": get_env_variable("PASSWORD_DB"),
        "HOST": get_env_variable("DB_HOST"),
        "PORT": get_env_variable("DB_PORT"),
        'OPTIONS': {
            'options': '-c statement_timeout={}'.format(get_env_variable("statement_timeout", 7000)),
        }
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
"""
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

"""
# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "es-cl"

LANGUAGES = (("en", "English"), ("es", "Spanish"))

#LOCALE_PATHS = (join(BASE_DIR, "locale"),)

TIME_ZONE = "America/Argentina/Buenos_Aires"  # "America/Santiago"

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL='userapp.UserApp'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
#STATIC_ROOT = "/home/brujula_user/brujula_backend/brujula/static/"
STATICFILES_DIRS = [
    "staticfiles",
]

# Cors
CORS_ORIGIN_ALLOW_ALL= True
#CORS_ORIGIN_WHITELIST = ["https://iris7.cl","https://devel.iris7.cl","https://demo.iris7.cl",]
CORS_ALLOW_METHODS = [ 'DELETE','GET','OPTIONS','PATCH','POST','PUT',]
ALLOWED_HOSTS=["*"]
CORS_ALLOW_HEADERS = ['accept','accept-encoding','authorization','content-type','dnt','origin','user-agent','x-csrftoken','x-requested-with',]
#End Cors


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CSRF_COOKIE_NAME = SITE_NAME + '_csrftoken'
CSRF_TRUSTED_ORIGINS = ['https://*.multifiberapp.com']


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    },
    'USE_SESSION_AUTH':False
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = get_env_variable('EMAIL_HOST_SMTP',"smtp.gmail.com")
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_PORT = 587

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND ='redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT =["application/json"]
CELERY_RESULT_SERIALIZER ='json'
CELERY_TASK_SELERLIZER ='json'
# CELERY_DEFAULT_QUEUE = 'queue1'
CELERY_TIMEZONE ="America/Argentina/Buenos_Aires"



SILENCED_SYSTEM_CHECKS = ['EM_001']