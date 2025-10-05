import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')
django.setup()

c = Client()
# Use credentials you created with createsuperuser
USERNAME = 'admin'
PASSWORD = 'admin'

print('Attempting login as', USERNAME)
login_success = c.login(username=USERNAME, password=PASSWORD)
print('login_success =', login_success)
resp = c.post('/dashboard/api/ml/scenarios/', data='{"scenario": "wildfire_nearby"}', content_type='application/json')
print('status =', resp.status_code)
print('content =', resp.content.decode('utf-8')[:1000])
