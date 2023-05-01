#!/bin/bash
SYSTEM_NAME=brujula
USER=${SYSTEM_NAME}_user # the user to run as
GROUP=$USER # the group to run as
NAME="Servidor_${SYSTEM_NAME}" # Name of the application
DJANGODIR=/home/$USER/${SYSTEM_NAME}_backend/${SYSTEM_NAME}/ # Django project directory
LOGFILE=/home/$USER/${SYSTEM_NAME}_backend/logs/gunicorn_${SYSTEM_NAME}.log
LOGDIR=$(dirname $LOGFILE)
SOCKFILE=/home/$USER/${SYSTEM_NAME}_backend/gunicorn.sock # we will communicate using this unix socket
LOGDIR_PROJECT=/home/$USER/${SYSTEM_NAME}_backend/logs # we will communicate using this unix socket

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

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
# Create the run directory if it doesn't exist for logs sentinel
test -d $LOGDIR_PROJECT || mkdir -p $LOGDIR_PROJECT

source /home/${SYSTEM_NAME}_user/${SYSTEM_NAME}_env/bin/activate

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /home/$USER/${SYSTEM_NAME}_env/bin/gunicorn \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--bind=127.0.0.1:$2 \
--log-level=debug \
--timeout $TIMEOUT \
--capture-output \
--log-file=$LOGFILE 2>>$LOGFILE \
${DJANGO_WSGI_MODULE}:application