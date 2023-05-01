from .base import *  # noqa
from os.path import dirname, join

ENVIROMENT = "PROD"
DEBUG = False

PRODUCTION_APPS = ["storages",]

#INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS + PRODUCTION_APPS

ALLOWED_HOSTS = ["*"]

STATIC_ROOT = "/home/marketplace/marketplace_backend/marketplace/static/"
MEDIA_ROOT = "/home/marketplace/marketplace_backend/marketplace/media/"

BASE_DIR_LOG = "/home/marketplace/marketplace_backend/marketplace/logs"


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
        'sqlformatter': {
            '()': 'ddquery.SqlFormatter',
            'format': '%(message)s %(asctime)s',
            'reindent': False,
            'highlight': False,
        },
    },    
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        'sqlhandler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'sqlformatter',
        },
        'sqlfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(BASE_DIR_LOG, 'debug_db.log'),
            'maxBytes': 1024*1024*8, # 8 MB
            'backupCount': 3,
            'formatter': 'sqlformat',
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
        'django.db.backends': {
            'handlers': ['sqlfile'],
            'level': 'DEBUG',
        },        
        "": {"level": "DEBUG", "handlers": ["console"],},
    },
}
