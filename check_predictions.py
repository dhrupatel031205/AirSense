#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')
django.setup()

from dashboard.models import MLPrediction, UserLocationPreference
from django.utils import timezone

print("=== ML Predictions Check ===")
print(f"Total predictions: {MLPrediction.objects.count()}")

locations = MLPrediction.objects.values_list('location', flat=True).distinct()
print(f"Locations with predictions: {list(locations)}")

print("\n=== User Locations ===")
user_locations = UserLocationPreference.objects.all()
for loc in user_locations:
    print(f"User: {loc.user.username}, Location: {loc.location_name}, Primary: {loc.is_primary}")

print("\n=== Sample Predictions ===")
now = timezone.now()
future_predictions = MLPrediction.objects.filter(prediction_for__gte=now).order_by('prediction_for')[:10]

for p in future_predictions:
    print(f"  {p.location}: {p.predicted_aqi} AQI at {p.prediction_for} (Model: {p.model_type})")

if not future_predictions:
    print("  No future predictions found!")
    print("\n=== All Predictions ===")
    all_preds = MLPrediction.objects.all()[:5]
    for p in all_preds:
        print(f"  {p.location}: {p.predicted_aqi} AQI at {p.prediction_for}")