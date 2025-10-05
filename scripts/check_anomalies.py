import os
import sys
sys.path.append(r"c:\Users\DHRUV PATEL\Downloads\AirSense-main\AirSense-main")
os.environ.setdefault('DJANGO_SETTINGS_MODULE','airquality_project.settings')
import django
django.setup()
from django.test import Client
c = Client()
resp = c.get('/dashboard/api/ml/anomalies/?location=New York, NY')
print('status', resp.status_code)
print(resp.content.decode())
