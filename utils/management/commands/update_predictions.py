from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import pandas as pd
from dashboard.models import AirQualityReading, MLPrediction, UserLocationPreference
from ml_models.ml_manager import MLModelManager
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update ML predictions for all locations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--initialize',
            action='store_true',
            help='Initialize ML models with historical data',
        )
        parser.add_argument(
            '--location',
            type=str,
            help='Update predictions for specific location only',
        )

    def handle(self, *args, **options):
        ml_manager = MLModelManager()
        
        if options['initialize']:
            self.stdout.write('Initializing ML models...')
            self.initialize_models(ml_manager)
        
        if options['location']:
            self.update_location_predictions(ml_manager, options['location'])
        else:
            self.update_all_predictions(ml_manager)

    def initialize_models(self, ml_manager):
        """Initialize ML models with historical data"""
        try:
            # Get historical data from the last 30 days
            cutoff_date = timezone.now() - timedelta(days=30)
            historical_readings = AirQualityReading.objects.filter(
                timestamp__gte=cutoff_date
            ).order_by('timestamp')
            
            if historical_readings.count() < 10:
                self.stdout.write(
                    self.style.WARNING('Not enough historical data. Creating sample data...')
                )
                self.create_sample_data()
                historical_readings = AirQualityReading.objects.filter(
                    timestamp__gte=cutoff_date
                ).order_by('timestamp')
            
            # Convert to DataFrame
            data = []
            for reading in historical_readings:
                data.append({
                    'timestamp': reading.timestamp,
                    'location': reading.location,
                    'aqi': reading.aqi_value,
                    'pm25': reading.concentration if reading.pollutant_type == 'PM2.5' else 0,
                    'pm10': reading.concentration if reading.pollutant_type == 'PM10' else 0,
                    'no2': reading.concentration if reading.pollutant_type == 'NO2' else 0,
                    'o3': reading.concentration if reading.pollutant_type == 'O3' else 0,
                })
            
            historical_data = pd.DataFrame(data)
            
            # Initialize models
            result = ml_manager.initialize_models(historical_data)
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'Models initialized successfully: {result["models_trained"]}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Model initialization failed: {result["error"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing models: {str(e)}')
            )

    def update_all_predictions(self, ml_manager):
        """Update predictions for all user locations"""
        locations = UserLocationPreference.objects.values_list('location_name', flat=True).distinct()
        
        if not locations:
            # Use default locations if no user preferences
            locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL']
            self.stdout.write(
                self.style.WARNING('No user locations found. Using default locations.')
            )
        
        for location in locations:
            self.update_location_predictions(ml_manager, location)

    def update_location_predictions(self, ml_manager, location):
        """Update predictions for a specific location"""
        try:
            self.stdout.write(f'Updating predictions for {location}...')
            
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
            
            # Save hourly forecasts if available
            if 'hourly_forecast' in predictions and predictions['hourly_forecast']:
                self.save_predictions(location, predictions['hourly_forecast'])
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {len(predictions["hourly_forecast"])} predictions for {location}')
                )
            else:
                # Create basic predictions if ML models aren't trained
                self.create_basic_predictions(location, location_data)
                self.stdout.write(
                    self.style.WARNING(f'Created basic predictions for {location} (ML models not trained)')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating predictions for {location}: {str(e)}')
            )

    def save_predictions(self, location, forecasts):
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

    def create_basic_predictions(self, location, current_data):
        """Create basic predictions when ML models aren't available"""
        base_aqi = current_data['aqi']
        now = timezone.now()
        
        # Clear old predictions
        MLPrediction.objects.filter(
            location=location,
            prediction_for__gte=now
        ).delete()
        
        # Create 24 hours of predictions with some variation
        import random
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

    def create_sample_data(self):
        """Create sample historical data for model training"""
        from datetime import datetime
        import random
        
        locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL']
        pollutants = ['PM2.5', 'PM10', 'NO2', 'O3']
        
        # Create data for the last 7 days
        base_time = timezone.now() - timedelta(days=7)
        
        for day in range(7):
            for hour in range(0, 24, 3):  # Every 3 hours
                timestamp = base_time + timedelta(days=day, hours=hour)
                
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
                        
                        AirQualityReading.objects.get_or_create(
                            location=location,
                            timestamp=timestamp,
                            pollutant_type=pollutant,
                            defaults={
                                'latitude': 40.7128,
                                'longitude': -74.0060,
                                'concentration': concentration,
                                'aqi_value': min(200, aqi),
                                'source': 'SAMPLE_DATA'
                            }
                        )
        
        self.stdout.write(
            self.style.SUCCESS('Created sample historical data for model training')
        )