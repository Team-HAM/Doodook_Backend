# yourproject/celery.py
import os
from tasks_celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myapi.settings')

app = Celery('doodook')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
