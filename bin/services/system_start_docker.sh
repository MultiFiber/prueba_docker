#!/bin/bash
SYSTEM_NAME=brujula
USER=root # the user to run as
GROUP=$USER # the group to run as
NAME="Servidor_${SYSTEM_NAME}" # Name of the application
DJANGODIR=/app/brujula/ # Django project directory
LOGFILE=/app/logs/gunicorn_${SYSTEM_NAME}_docker.log
LOGDIR=$(dirname $LOGFILE)

NUM_CPUS=$(nproc --all) # 3 how many worker processes should Gunicorn spawn
NUM_WORKERS=6;
DJANGO_SETTINGS_MODULE=config.settings.$1 # which settings file should Django use
DJANGO_WSGI_MODULE=config.wsgi
TIMEOUT=600

# if [ $NUM_CPUS -eq 2 ]
# then
# 	NUM_WORKERS=2;
# else
# 	NUM_WORKERS= NUM_CPUS - 2;
# fi

echo "Starting $NAME as `whoami` DJANGO_SETTINGS_MODULE=$1 PORT $2"

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

gunicorn \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=0.0.0.0:$2 \
--log-level=debug \
--timeout $TIMEOUT \
--capture-output \
--log-file=$LOGFILE 2>>$LOGFILE \
${DJANGO_WSGI_MODULE}:application