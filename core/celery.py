import os

from celery import Celery


# Init
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules
app.autodiscover_tasks(['utils'])