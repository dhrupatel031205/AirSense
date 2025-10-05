from django.core.management.base import BaseCommand
from django.test import Client
import random

class Command(BaseCommand):
    help = 'Test registration and login endpoints using Django test client'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=None)
        parser.add_argument('--password', default='Testpass123')

    def handle(self, *args, **options):
        username = options['username'] or f'testuser_{random.randint(1000,9999)}'
        password = options['password']

        c = Client()
        self.stdout.write('GET /auth/register/')
        get_resp = c.get('/auth/register/', **{'HTTP_HOST': 'localhost'})
        self.stdout.write(f'GET status: {get_resp.status_code}')

        # Now POST to register
        data = {
            'username': username,
            'email': f'{username}@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': password,
            'password2': password,
            'terms': 'on'
        }
        post_resp = c.post('/auth/register/', data=data, **{'HTTP_HOST': 'localhost'})
        self.stdout.write(f'POST register status: {post_resp.status_code}')
        self.stdout.write(f'POST register location/header: {post_resp.get('Location', '')}')

        # Try to login with created credentials
        login_resp = c.post('/auth/login/', data={'username': username, 'password': password}, **{'HTTP_HOST': 'localhost'})
        self.stdout.write(f'POST login status: {login_resp.status_code}')
        self.stdout.write(f'Login content (first 300 chars): {login_resp.content.decode("utf-8")[:300]}')
