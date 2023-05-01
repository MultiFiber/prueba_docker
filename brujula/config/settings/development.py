import os
from .base import *  # noqa

ENVIROMENT = "DEV"
DEBUG = True
DEVELOPMENT_APPS = []

#INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS + DEVELOPMENT_APPS

ALLOWED_HOSTS = ["*"]

#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

MEDIA_URL = '/media/'
STATIC_ROOT = "/home/brujula_user/brujula_backend/brujula/static/"
MEDIA_ROOT = "/home/brujula_user/brujula_backend/brujula/media/"
BASE_DIR_LOG = "/home/brujula_user/brujula_backend/logs"

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
            "class":"logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            'maxBytes': 1024*1024*1, # 1 MB
            "filename": os.path.join(BASE_DIR_LOG, "debug_django.log"),
        },
    },
    "loggers": {
        'django.request': {
            'handlers': ['file','console'],
            'level': 'DEBUG',
        }
    },
}