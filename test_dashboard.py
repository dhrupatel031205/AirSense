#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from dashboard.models import UserLocationPreference, MLPrediction
from django.utils import timezone

# Create test client
client = Client()

# Get or create demo user
try:
    user = User.objects.get(username='demo')
    print(f"Found demo user: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_user('demo', 'demo@test.com', 'demo123')
    print("Created demo user")

# Login
client.login(username='demo', password='demo123')

# Test dashboard view
try:
    response = client.get('/dashboard/')
    print(f"Dashboard response status: {response.status_code}")
    
    if response.status_code == 200:
        print("Dashboard loads successfully")
        
        # Check if predictions data is in context
        if hasattr(response, 'context') and response.context:
            predictions_data = response.context.get('predictions_data', [])
            chart_data = response.context.get('chart_data', '{}')
            
            print(f"Predictions data count: {len(predictions_data)}")
            print(f"Chart data: {chart_data}")
            
            if predictions_data:
                print("Real predictions found in context")
                for i, pred in enumerate(predictions_data):
                    print(f"  {pred['hours_ahead']}h: {pred['aqi']} AQI ({pred['category']})")
            else:
                print("WARNING: No predictions data in context")
        else:
            print("WARNING: No context data available")
    else:
        print(f"ERROR: Dashboard failed to load: {response.status_code}")
        
except Exception as e:
    print(f"ERROR: Error testing dashboard: {e}")

# Check predictions in database
print(f"\nDatabase check:")
print(f"Total predictions: {MLPrediction.objects.count()}")
future_preds = MLPrediction.objects.filter(prediction_for__gte=timezone.now())
print(f"Future predictions: {future_preds.count()}")

# Check user locations
user_locs = UserLocationPreference.objects.filter(user=user)
print(f"User locations: {user_locs.count()}")
for loc in user_locs:
    print(f"  - {loc.location_name} (Primary: {loc.is_primary})")
    
    # Check predictions for this location
    loc_preds = MLPrediction.objects.filter(
        location=loc.location_name,
        prediction_for__gte=timezone.now()
    ).count()
    print(f"    Predictions: {loc_preds}")