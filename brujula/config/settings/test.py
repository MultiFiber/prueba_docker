from .base import *  # noqa
from os.path import dirname, join
import os

ENVIROMENT = "PROD"
DEBUG = True

PRODUCTION_APPS = ["storages",]

#INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS + PRODUCTION_APPS

ALLOWED_HOSTS = ["*"]

STATIC_ROOT = "static/"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

BASE_DIR_LOG = "../logs"


LOGGING = {
    "version": 1,
    "formatters": {
        'sqlformat': {
            'format': '{asctime} {message}',
            'style': '{'
        },
        "verbose": {
            "format": "%(levelname)s:%(name)s: %(message)s"
        },
       
    },    
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    
        "file": {
            "level": "INFO",
            #"class": "logging.FileHandler",
            "class":"logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            'maxBytes': 1024*1024*1, # 1 MB
            "filename": join(BASE_DIR_LOG, "debug_django.log"),
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "matplotlib": {
            "handlers": ["file", "console"],
            "level": "ERROR",
            "propagate": False,
        },
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        # },        
        "": {"level": "DEBUG", "handlers": ["console"],},
    },
}

DATABASES = {

    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": get_env_variable("TEST_DB_NAME"),
        "USER": get_env_variable("TEST_DB_USER"),
        "PASSWORD": get_env_variable("TEST_PASSWORD_DB",),
        "HOST": get_env_variable("TEST_DB_HOST", "localhost"),
        "PORT": get_env_variable("TEST_DB_PORT", 5432),
        'OPTIONS': {
            'options': '-c statement_timeout={}'.format(get_env_variable("statement_timeout", 7000)),
        }
    },
}



_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


ROOT_URLCONF = 'config.urls_test'