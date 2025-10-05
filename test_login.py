#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create test client
client = Client()

print("=== Login System Test ===")

# Test 1: Check if demo user exists
try:
    demo_user = User.objects.get(username='demo')
    print(f"Demo user exists: {demo_user.username}")
except User.DoesNotExist:
    print("Demo user not found, creating...")
    demo_user = User.objects.create_user('demo', 'demo@test.com', 'demo123')
    print(f"Created demo user: {demo_user.username}")

# Test 2: Check login page loads
response = client.get('/users/login/')
print(f"Login page status: {response.status_code}")
if response.status_code == 200:
    print("Login page loads successfully")
else:
    print("Login page failed to load")

# Test 3: Test login functionality
login_data = {
    'username': 'demo',
    'password': 'demo123'
}

response = client.post('/users/login/', login_data, follow=True)
print(f"Login POST status: {response.status_code}")

if response.status_code == 200:
    # Check if we're redirected to dashboard
    if 'dashboard' in response.request['PATH_INFO']:
        print("Login successful - redirected to dashboard")
    else:
        print(f"Login response path: {response.request['PATH_INFO']}")
        print("? Login may have succeeded but redirect unclear")
else:
    print("Login failed")

# Test 4: Check if user is authenticated after login
if hasattr(response, 'wsgi_request') and hasattr(response.wsgi_request, 'user'):
    if response.wsgi_request.user.is_authenticated:
        print(f"User authenticated: {response.wsgi_request.user.username}")
    else:
        print("User not authenticated after login")

print("\n=== URL Test ===")
print("Testing key URLs:")

urls_to_test = [
    '/users/login/',
    '/users/register/',
    '/dashboard/',
    '/scenario-simulator/',
    '/eco-action/',
    '/social-impact/',
    '/health-alerts/settings/'
]

for url in urls_to_test:
    try:
        response = client.get(url)
        status = "OK" if response.status_code in [200, 302] else "FAIL"
        print(f"{status} {url} - Status: {response.status_code}")
    except Exception as e:
        print(f"FAIL {url} - Error: {e}")

print("\n=== Summary ===")
print("If login page loads (200) and login POST succeeds, the system should work.")
print("Try logging in with: demo / demo123")