"""
Utility functions for ML models and data processing
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import AirQualityReading, MLPrediction
from .cnn_model import get_cnn_prediction
from .regression_model import get_regression_prediction


def get_location_predictions(location, hours_ahead=24):
    """
    Get ML predictions for a location for the next N hours
    
    Args:
        location: Location name
        hours_ahead: Number of hours to predict ahead
        
    Returns:
        List of prediction dictionaries
    """
    predictions = []
    current_time = timezone.now()
    
    for hour in range(1, hours_ahead + 1):
        prediction_time = current_time + timedelta(hours=hour)
        
        # Get weather forecast for this time (placeholder)
        weather_data = get_weather_forecast(location, prediction_time)
        
        # Get historical data for context
        historical_data = get_historical_context(location, current_time)
        
        # Try regression model first (faster and more reliable for short-term)
        regression_result = get_regression_prediction(location, weather_data, historical_data)
        
        if regression_result.get('prediction') is not None:
            prediction = {
                'location': location,
                'prediction_time': prediction_time,
                'aqi_prediction': regression_result['prediction'],
                'confidence': regression_result['confidence'],
                'model_type': regression_result['model_type'],
                'hour_ahead': hour
            }
            predictions.append(prediction)
            
            # Save to database
            save_prediction_to_db(prediction)
    
    return predictions


def get_weather_forecast(location, target_time):
    """
    Get weather forecast data for a location and time
    
    Args:
        location: Location name
        target_time: Target datetime for forecast
        
    Returns:
        Dictionary with weather data
    """
    # Placeholder implementation
    # In a real scenario, this would call weather APIs
    
    import random
    
    return {
        'temperature': random.uniform(15, 35),
        'humidity': random.uniform(30, 90),
        'pressure': random.uniform(1000, 1030),
        'wind_speed': random.uniform(0, 20),
        'wind_direction': random.uniform(0, 360),
        'precipitation': random.uniform(0, 10),
        'timestamp': target_time,
        'latitude': 0.0,  # Should be actual coordinates
        'longitude': 0.0,
        'elevation': 100.0
    }


def get_historical_context(location, current_time):
    """
    Get historical air quality data for context
    
    Args:
        location: Location name
        current_time: Current datetime
        
    Returns:
        Dictionary with historical averages
    """
    # Get data from the last 24 hours
    start_time = current_time - timedelta(hours=24)
    
    historical_readings = AirQualityReading.objects.filter(
        location=location,
        timestamp__gte=start_time,
        timestamp__lte=current_time
    ).order_by('-timestamp')
    
    if not historical_readings.exists():
        # Return default values if no historical data
        return {
            'pm25_1h_avg': 25.0,
            'pm25_24h_avg': 25.0,
            'pm10_1h_avg': 45.0,
            'no2_1h_avg': 20.0
        }
    
    # Calculate averages for different time windows
    pm25_readings = historical_readings.filter(pollutant_type='PM2.5')
    pm10_readings = historical_readings.filter(pollutant_type='PM10')
    no2_readings = historical_readings.filter(pollutant_type='NO2')
    
    # 1-hour average (last hour)
    one_hour_ago = current_time - timedelta(hours=1)
    pm25_1h = pm25_readings.filter(timestamp__gte=one_hour_ago)
    
    # 24-hour average
    pm25_24h = pm25_readings
    
    return {
        'pm25_1h_avg': calculate_avg_concentration(pm25_1h),
        'pm25_24h_avg': calculate_avg_concentration(pm25_24h),
        'pm10_1h_avg': calculate_avg_concentration(pm10_readings),
        'no2_1h_avg': calculate_avg_concentration(no2_readings)
    }


def calculate_avg_concentration(readings):
    """Calculate average concentration from readings"""
    if not readings.exists():
        return 0.0
    
    concentrations = [reading.concentration for reading in readings]
    return sum(concentrations) / len(concentrations)


def save_prediction_to_db(prediction):
    """
    Save ML prediction to database
    
    Args:
        prediction: Prediction dictionary
    """
    try:
        ml_prediction = MLPrediction(
            location=prediction['location'],
            latitude=0.0,  # Should get actual coordinates
            longitude=0.0,
            pollutant_type='PM2.5',  # Default, should be configurable
            predicted_concentration=prediction['aqi_prediction'],
            predicted_aqi=prediction['aqi_prediction'],
            confidence_score=prediction['confidence'],
            prediction_horizon_hours=prediction['hour_ahead'],
            model_type=prediction['model_type'],
            prediction_for=prediction['prediction_time']
        )
        ml_prediction.save()
        
    except Exception as e:
        print(f"Error saving prediction to database: {e}")


def calculate_aqi_from_concentration(concentration, pollutant_type):
    """
    Calculate AQI from pollutant concentration
    
    Args:
        concentration: Pollutant concentration value
        pollutant_type: Type of pollutant (PM2.5, PM10, etc.)
        
    Returns:
        AQI value (0-500)
    """
    # Simplified AQI calculation
    # In reality, this would use official EPA breakpoints
    
    if pollutant_type == 'PM2.5':
        # PM2.5 breakpoints (μg/m³)
        if concentration <= 12.0:
            return int((50 / 12.0) * concentration)
        elif concentration <= 35.4:
            return int(50 + ((100 - 50) / (35.4 - 12.1)) * (concentration - 12.1))
        elif concentration <= 55.4:
            return int(100 + ((150 - 100) / (55.4 - 35.5)) * (concentration - 35.5))
        elif concentration <= 150.4:
            return int(150 + ((200 - 150) / (150.4 - 55.5)) * (concentration - 55.5))
        elif concentration <= 250.4:
            return int(200 + ((300 - 200) / (250.4 - 150.5)) * (concentration - 150.5))
        else:
            return min(500, int(300 + ((500 - 300) / (500.4 - 250.5)) * (concentration - 250.5)))
    
    elif pollutant_type == 'PM10':
        # PM10 breakpoints (μg/m³)
        if concentration <= 54:
            return int((50 / 54) * concentration)
        elif concentration <= 154:
            return int(50 + ((100 - 50) / (154 - 55)) * (concentration - 55))
        elif concentration <= 254:
            return int(100 + ((150 - 100) / (254 - 155)) * (concentration - 155))
        elif concentration <= 354:
            return int(150 + ((200 - 150) / (354 - 255)) * (concentration - 255))
        elif concentration <= 424:
            return int(200 + ((300 - 200) / (424 - 355)) * (concentration - 355))
        else:
            return min(500, int(300 + ((500 - 300) / (604 - 425)) * (concentration - 425)))
    
    else:
        # Default calculation for other pollutants
        return min(500, max(0, int(concentration * 2)))


def get_aqi_category(aqi_value):
    """
    Get AQI category and color based on value
    
    Args:
        aqi_value: AQI numeric value
        
    Returns:
        Dictionary with category info
    """
    if aqi_value <= 50:
        return {
            'category': 'Good',
            'color': '#00E400',
            'description': 'Air quality is considered satisfactory'
        }
    elif aqi_value <= 100:
        return {
            'category': 'Moderate',
            'color': '#FFFF00',
            'description': 'Air quality is acceptable for most people'
        }
    elif aqi_value <= 150:
        return {
            'category': 'Unhealthy for Sensitive Groups',
            'color': '#FF7E00',
            'description': 'Sensitive people may experience minor issues'
        }
    elif aqi_value <= 200:
        return {
            'category': 'Unhealthy',
            'color': '#FF0000',
            'description': 'Everyone may begin to experience health effects'
        }
    elif aqi_value <= 300:
        return {
            'category': 'Very Unhealthy',
            'color': '#8F3F97',
            'description': 'Health warnings of emergency conditions'
        }
    else:
        return {
            'category': 'Hazardous',
            'color': '#7E0023',
            'description': 'Emergency conditions: everyone affected'
        }


def validate_prediction_input(data):
    """
    Validate input data for ML prediction
    
    Args:
        data: Input data dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['location', 'timestamp']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate location
    if not isinstance(data['location'], str) or len(data['location']) == 0:
        return False, "Location must be a non-empty string"
    
    # Validate timestamp
    try:
        if isinstance(data['timestamp'], str):
            datetime.fromisoformat(data['timestamp'])
    except ValueError:
        return False, "Invalid timestamp format"
    
    return True, None