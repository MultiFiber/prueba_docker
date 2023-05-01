import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.docker_local')

app = Celery('config')


app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    from datetime import datetime
    from operator_setting.models import KeyValueSystem
    KeyValueSystem.objects.create(name=f'debug_task_',value={'value':f'ejecutada con exito {str(datetime.now())}'})
    return True