from django.core.management.base import BaseCommand
from django.test import Client

class Command(BaseCommand):
    help = 'Test POST to dashboard scenario_simulation API using test client'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin')
        parser.add_argument('--password', default='admin')
        parser.add_argument('--scenario', default='wildfire_nearby')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        scenario = options['scenario']

        c = Client()
        logged_in = c.login(username=username, password=password)
        self.stdout.write(f'login: {logged_in}')

        # Provide HTTP_HOST to avoid DisallowedHost when using the test client
        resp = c.post('/dashboard/api/ml/scenarios/', data='{"scenario": "%s"}' % scenario, content_type='application/json', **{'HTTP_HOST': 'localhost'})
        self.stdout.write(f'status: {resp.status_code}')
        self.stdout.write(f'content: {resp.content.decode("utf-8")[:200]}')
