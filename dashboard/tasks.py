from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AirQualityReading, MLPrediction, UserLocationPreference
from ml_models.ml_manager import MLModelManager
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_ml_predictions():
    """Celery task to update ML predictions for all locations"""
    try:
        ml_manager = MLModelManager()
        
        # Get all user locations
        locations = UserLocationPreference.objects.values_list('location_name', flat=True).distinct()
        
        if not locations:
            locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL']
        
        updated_count = 0
        for location in locations:
            try:
                # Get latest reading for this location
                latest_reading = AirQualityReading.objects.filter(
                    location=location
                ).first()
                
                if not latest_reading:
                    # Create mock current data
                    location_data = {
                        'location': location,
                        'aqi': 73,
                        'pm25': 25,
                        'pm10': 35,
                        'no2': 45,
                        'o3': 55,
                        'temperature': 24,
                        'humidity': 65,
                        'wind_speed': 15
                    }
                else:
                    location_data = {
                        'location': location,
                        'aqi': latest_reading.aqi_value,
                        'pm25': latest_reading.concentration if latest_reading.pollutant_type == 'PM2.5' else 25,
                        'pm10': latest_reading.concentration if latest_reading.pollutant_type == 'PM10' else 35,
                        'no2': latest_reading.concentration if latest_reading.pollutant_type == 'NO2' else 45,
                        'o3': latest_reading.concentration if latest_reading.pollutant_type == 'O3' else 55,
                        'temperature': 24,
                        'humidity': 65,
                        'wind_speed': 15
                    }
                
                # Get predictions
                predictions = ml_manager.get_real_time_predictions(location_data)
                
                # Save predictions
                if 'hourly_forecast' in predictions and predictions['hourly_forecast']:
                    save_ml_predictions(location, predictions['hourly_forecast'])
                else:
                    create_basic_predictions(location, location_data)
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating predictions for {location}: {str(e)}")
                continue
        
        logger.info(f"Updated predictions for {updated_count} locations")
        return f"Updated predictions for {updated_count} locations"
        
    except Exception as e:
        logger.error(f"Error in update_ml_predictions task: {str(e)}")
        raise

def save_ml_predictions(location, forecasts):
    """Save ML predictions to database"""
    # Clear old predictions for this location
    MLPrediction.objects.filter(
        location=location,
        prediction_for__gte=timezone.now()
    ).delete()
    
    # Save new predictions
    for forecast in forecasts:
        MLPrediction.objects.create(
            location=location,
            latitude=40.7128,  # Default coordinates
            longitude=-74.0060,
            pollutant_type='PM2.5',
            predicted_concentration=forecast.get('predicted_concentration', 25),
            predicted_aqi=forecast['predicted_aqi'],
            confidence_score=forecast.get('confidence', 0.8),
            prediction_horizon_hours=forecast.get('hours_ahead', 1),
            model_type='ML_ENSEMBLE',
            prediction_for=forecast['timestamp']
        )

def create_basic_predictions(location, current_data):
    """Create basic predictions when ML models aren't available"""
    import random
    
    base_aqi = current_data['aqi']
    now = timezone.now()
    
    # Clear old predictions
    MLPrediction.objects.filter(
        location=location,
        prediction_for__gte=now
    ).delete()
    
    # Create 24 hours of predictions with some variation
    for hour in range(1, 25):
        # Add some random variation
        variation = random.randint(-10, 10)
        predicted_aqi = max(10, min(200, base_aqi + variation))
        
        MLPrediction.objects.create(
            location=location,
            latitude=40.7128,
            longitude=-74.0060,
            pollutant_type='PM2.5',
            predicted_concentration=predicted_aqi * 0.5,
            predicted_aqi=predicted_aqi,
            confidence_score=0.6,
            prediction_horizon_hours=hour,
            model_type='BASIC',
            prediction_for=now + timedelta(hours=hour)
        )

@shared_task
def cleanup_old_predictions():
    """Clean up old predictions to keep database size manageable"""
    cutoff_date = timezone.now() - timedelta(days=7)
    deleted_count = MLPrediction.objects.filter(
        prediction_for__lt=cutoff_date
    ).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old predictions")
    return f"Cleaned up {deleted_count} old predictions"

@shared_task
def fetch_real_air_quality_data():
    """Fetch real air quality data from external APIs"""
    # This would integrate with NASA TEMPO, EPA, or other APIs
    # For now, we'll create sample data
    import random
    from datetime import datetime
    
    locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL']
    pollutants = ['PM2.5', 'PM10', 'NO2', 'O3']
    
    created_count = 0
    for location in locations:
        for pollutant in pollutants:
            # Generate realistic values
            if pollutant == 'PM2.5':
                concentration = random.randint(10, 50)
                aqi = int(concentration * 2)
            elif pollutant == 'PM10':
                concentration = random.randint(20, 80)
                aqi = int(concentration * 1.5)
            elif pollutant == 'NO2':
                concentration = random.randint(20, 100)
                aqi = int(concentration * 1.2)
            else:  # O3
                concentration = random.randint(30, 120)
                aqi = int(concentration * 1.1)
            
            reading, created = AirQualityReading.objects.get_or_create(
                location=location,
                timestamp=timezone.now().replace(minute=0, second=0, microsecond=0),
                pollutant_type=pollutant,
                defaults={
                    'latitude': 40.7128,
                    'longitude': -74.0060,
                    'concentration': concentration,
                    'aqi_value': min(200, aqi),
                    'source': 'API_SIMULATION'
                }
            )
            
            if created:
                created_count += 1
    
    logger.info(f"Created {created_count} new air quality readings")
    return f"Created {created_count} new air quality readings"