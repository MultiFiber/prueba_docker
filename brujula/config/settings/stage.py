from .base import *  # noqa
from os.path import dirname, join

ENVIROMENT = "STAGE"
DEBUG = True

PRODUCTION_APPS = []

#INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS + PRODUCTION_APPS

ALLOWED_HOSTS = ["*"]
MEDIA_URL = '/media/'
STATIC_ROOT = "/home/brujula_user/brujula_backend/brujula/static/"
MEDIA_ROOT = "/home/brujula_user/brujula_backend/brujula/media/"
BASE_DIR_LOG = "/home/brujula_user/brujula_backend/logs"

LOGGING = {
    "version": 1,
    "formatters": {"verbose": {"format": "%(levelname)s:%(name)s: %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": join(BASE_DIR_LOG, "debug_django.log"),
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "": {"level": "DEBUG", "handlers": ["console"],},
    },
}
