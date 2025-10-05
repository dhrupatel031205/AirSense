#!/usr/bin/env python
"""
Quick setup script to initialize the AirSense system
Run this after setting up the database to get the system working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from dashboard.models import UserLocationPreference

def main():
    print("Initializing AirSense System...")
    
    # 1. Create sample data and initialize ML models
    print("\nCreating sample data and initializing ML models...")
    try:
        call_command('update_predictions', '--initialize')
        print("ML models initialized successfully")
    except Exception as e:
        print(f"ML initialization warning: {e}")
    
    # 2. Update predictions for all locations
    print("\nGenerating initial predictions...")
    try:
        call_command('update_predictions')
        print("Predictions generated successfully")
    except Exception as e:
        print(f"Prediction generation warning: {e}")
    
    # 3. Create default user locations if none exist
    print("\nSetting up default locations...")
    if not UserLocationPreference.objects.exists():
        # Create a demo user if none exists
        if not User.objects.exists():
            User.objects.create_user(
                username='demo',
                email='demo@airsense.com',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )
            print("Created demo user (username: demo, password: demo123)")
        
        demo_user = User.objects.first()
        
        # Create default locations
        default_locations = [
            {'name': 'New York, NY', 'lat': 40.7128, 'lng': -74.0060, 'primary': True},
            {'name': 'Los Angeles, CA', 'lat': 34.0522, 'lng': -118.2437, 'primary': False},
            {'name': 'Chicago, IL', 'lat': 41.8781, 'lng': -87.6298, 'primary': False},
        ]
        
        for loc in default_locations:
            UserLocationPreference.objects.create(
                user=demo_user,
                location_name=loc['name'],
                latitude=loc['lat'],
                longitude=loc['lng'],
                is_primary=loc['primary']
            )
        
        print("Created default user locations")
    else:
        print("User locations already exist")
    
    print("\nSystem initialization complete!")
    print("\nNext steps:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://127.0.0.1:8000/")
    print("3. Login with demo/demo123 or create a new account")
    print("\nFor automatic predictions, also run:")
    print("- celery -A airquality_project worker --loglevel=info")
    print("- celery -A airquality_project beat --loglevel=info")

if __name__ == '__main__':
    main()