from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AirQualityReading, UserLocationPreference, MLPrediction
from .forms import LocationPreferenceForm
from .serializers import (
    AirQualityReadingSerializer, 
    UserLocationPreferenceSerializer, 
    MLPredictionSerializer
)
from .decorators import guest_allowed, authenticated_required
from .ml.utils import get_location_predictions
from utils.api_clients import fetch_current_air_quality
from ml_models.ml_manager import MLModelManager
import json
import pandas as pd


@guest_allowed
def dashboard_home(request):
    """Main dashboard view with ML predictions - supports guest users"""
    ml_manager = MLModelManager()

    # Get user's primary location or default (guest users get default location)
    if request.user.is_authenticated:
        user_location = UserLocationPreference.objects.filter(
            user=request.user, is_primary=True
        ).first()
        location_name = user_location.location_name if user_location else 'New York, NY'
    else:
        location_name = 'New York, NY'  # Default for guest users
    
    # Mock current data (in production, fetch from APIs)
    location_data = {
        'location': location_name,
        'aqi': 73,
        'pm25': 25,
        'pm10': 35,
        'no2': 45,
        'o3': 55,
        'temperature': 24,
        'humidity': 65,
        'wind_speed': 15
    }
    
    # Get user profile for personalized recommendations
    user_profile = {
        'age': getattr(request.user, 'age', 30),
        'conditions': []  # Would come from user health profile
    }
    
    # Get ML predictions and recommendations
    try:
        # Initialize models if not already done
        model_status = ml_manager.get_model_status()
        if not any(model_status['models_trained'].values()):
            # Try to initialize with existing data
            from django.utils import timezone
            from datetime import timedelta
            cutoff_date = timezone.now() - timedelta(days=7)
            historical_readings = AirQualityReading.objects.filter(
                timestamp__gte=cutoff_date
            ).order_by('timestamp')
            
            if historical_readings.count() >= 10:
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
                ml_manager.initialize_models(historical_data)
        
        predictions = ml_manager.get_real_time_predictions(location_data, user_profile)
        daily_summary = ml_manager.generate_daily_summary(location_data, user_profile)
    except Exception as e:
        # Provide fallback predictions
        predictions = {
            'health_recommendations': {
                'category': 'moderate',
                'severity_color': '#f59e0b',
                'recommendations': ['Monitor air quality conditions and limit prolonged outdoor activities.']
            }
        }
        daily_summary = {
            'category': 'Moderate',
            'forecast': {
                'trend': 'stable',
                'max_aqi': location_data['aqi'] + 10,
                'min_aqi': location_data['aqi'] - 10
            }
        }
    
    # Get prediction data for display
    predictions_data = []
    # Try exact match first, then partial match
    ml_predictions_qs = MLPrediction.objects.filter(
        location=location_name,
        prediction_for__gte=timezone.now()
    ).order_by('prediction_for')[:4]
    
    # If no exact match, try partial match
    if not ml_predictions_qs.exists():
        ml_predictions_qs = MLPrediction.objects.filter(
            location__icontains=location_name.split(',')[0],  # Just city name
            prediction_for__gte=timezone.now()
        ).order_by('prediction_for')[:4]
    
    for i, pred in enumerate(ml_predictions_qs):
        category = 'Good' if pred.predicted_aqi < 50 else 'Moderate' if pred.predicted_aqi < 100 else 'Unhealthy'
        predictions_data.append({
            'hours_ahead': (i + 1) * 6,  # 6, 12, 18, 24 hours
            'aqi': pred.predicted_aqi,
            'category': category,
            'timestamp': pred.prediction_for
        })
    
    # Chart data for JavaScript
    if predictions_data:
        chart_data = {
            'labels': [p['hours_ahead'] for p in predictions_data],
            'data': [p['aqi'] for p in predictions_data]
        }
    else:
        # Fallback data
        chart_data = {
            'labels': [6, 12, 18, 24],
            'data': [45, 68, 89, 125]
        }
    
    # Debug info
    print(f"Debug: Location: {location_name}")
    print(f"Debug: Predictions found: {ml_predictions_qs.count()}")
    print(f"Debug: Predictions data: {predictions_data}")
    print(f"Debug: Chart data: {chart_data}")
    
    context = {
        'current_aqi': location_data['aqi'],
        'aqi_category': 'Moderate',
        'location': location_name,
        'current_time': timezone.now(),
        'is_guest': not request.user.is_authenticated,
        'weather': {
            'temperature': location_data['temperature'],
            'condition': 'Partly Cloudy',
            'humidity': location_data['humidity'],
            'wind_speed': location_data['wind_speed'],
            'visibility': 10,
            'pressure': 1013
        },
        'ml_predictions': predictions,
        'daily_summary': daily_summary,
        'model_status': ml_manager.get_model_status(),
        'has_predictions': ml_predictions_qs.exists(),
        'predictions_data': predictions_data,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'dashboard/home.html', context)


# Alias for compatibility
home = dashboard_home


@guest_allowed
def guest_info(request):
    """Information page for guest users"""
    context = {
        'title': 'Guest Access - AirSense',
    }
    return render(request, 'dashboard/guest_info.html', context)


@authenticated_required
def air_quality_monitoring(request):
    """Air quality monitoring page with real-time data"""
    user_locations = UserLocationPreference.objects.filter(user=request.user)
    
    context = {
        'title': 'Air Quality Monitoring',
        'user_locations': user_locations,
    }
    return render(request, 'dashboard/monitoring.html', context)


@authenticated_required
def ml_predictions(request):
    """ML predictions page"""
    user_locations = UserLocationPreference.objects.filter(user=request.user)
    predictions = []
    
    for location in user_locations:
        location_predictions = MLPrediction.objects.filter(
            location=location.location_name
        )[:5]  # Get latest 5 predictions
        predictions.extend(location_predictions)
    
    context = {
        'title': 'ML Predictions',
        'predictions': predictions,
    }
    return render(request, 'dashboard/predictions.html', context)


@authenticated_required
def user_locations(request):
    """Manage user location preferences"""
    locations = UserLocationPreference.objects.filter(user=request.user)
    
    context = {
        'title': 'My Locations',
        'locations': locations,
    }
    return render(request, 'dashboard/locations.html', context)


@authenticated_required
def add_location(request):
    """Add a new location preference"""
    if request.method == 'POST':
        form = LocationPreferenceForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.user = request.user
            location.save()
            messages.success(request, 'Location added successfully!')
            return redirect('dashboard:locations')
    else:
        form = LocationPreferenceForm()
    
    context = {
        'title': 'Add Location',
        'form': form,
    }
    return render(request, 'dashboard/add_location.html', context)


@authenticated_required
def delete_location(request, location_id):
    """Delete a location preference"""
    location = get_object_or_404(UserLocationPreference, id=location_id, user=request.user)
    location.delete()
    messages.success(request, 'Location removed successfully!')
    return redirect('dashboard:locations')


# API Views
class AirQualityReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for air quality readings"""
    queryset = AirQualityReading.objects.all()
    serializer_class = AirQualityReadingSerializer


class MLPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset for ML predictions"""
    queryset = MLPrediction.objects.all()
    serializer_class = MLPredictionSerializer


@api_view(['GET'])
def get_current_aqi(request, location):
    """Get current AQI for a location"""
    try:
        latest_reading = AirQualityReading.objects.filter(
            location=location
        ).first()
        
        if latest_reading:
            return Response({
                'location': location,
                'aqi': latest_reading.aqi_value,
                'pollutant': latest_reading.pollutant_type,
                'concentration': latest_reading.concentration,
                'timestamp': latest_reading.timestamp,
            })
        else:
            return Response({
                'error': 'No data available for this location'
            }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_forecast(request, location):
    """Get ML forecast for a location"""
    try:
        predictions = MLPrediction.objects.filter(
            location=location,
            prediction_for__gte=timezone.now()
        )[:24]  # Next 24 hours
        
        forecast_data = []
        for pred in predictions:
            forecast_data.append({
                'timestamp': pred.prediction_for,
                'aqi': pred.predicted_aqi,
                'pollutant': pred.pollutant_type,
                'confidence': pred.confidence_score,
            })
        
        return Response({
            'location': location,
            'forecast': forecast_data,
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)