import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghana_decides_proj.settings')
app = Celery('ghana_decides_proj')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()