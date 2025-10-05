import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')

app = Celery('airquality_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'update-ml-predictions': {
        'task': 'dashboard.tasks.update_ml_predictions',
        'schedule': 3600.0,  # Run every hour
    },
    'fetch-air-quality-data': {
        'task': 'dashboard.tasks.fetch_real_air_quality_data',
        'schedule': 1800.0,  # Run every 30 minutes
    },
    'cleanup-old-predictions': {
        'task': 'dashboard.tasks.cleanup_old_predictions',
        'schedule': 86400.0,  # Run daily
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')