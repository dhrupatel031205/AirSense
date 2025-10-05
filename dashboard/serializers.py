from rest_framework import serializers
from .models import AirQualityReading, UserLocationPreference, MLPrediction


class AirQualityReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirQualityReading
        fields = [
            'id', 'location', 'latitude', 'longitude', 'pollutant_type',
            'concentration', 'aqi_value', 'timestamp', 'source', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserLocationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocationPreference
        fields = [
            'id', 'location_name', 'latitude', 'longitude', 
            'is_primary', 'alert_threshold', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MLPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLPrediction
        fields = [
            'id', 'location', 'latitude', 'longitude', 'pollutant_type',
            'predicted_concentration', 'predicted_aqi', 'confidence_score',
            'prediction_horizon_hours', 'model_type', 'created_at', 'prediction_for'
        ]
        read_only_fields = ['id', 'created_at']


class CurrentAQISerializer(serializers.Serializer):
    location = serializers.CharField(max_length=100)
    aqi = serializers.IntegerField()
    pollutant = serializers.CharField(max_length=10)
    concentration = serializers.FloatField()
    timestamp = serializers.DateTimeField()
    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    
    def get_category(self, obj):
        aqi = obj.get('aqi', 0)
        if aqi <= 50:
            return 'Good'
        elif aqi <= 100:
            return 'Moderate'
        elif aqi <= 150:
            return 'Unhealthy for Sensitive Groups'
        elif aqi <= 200:
            return 'Unhealthy'
        elif aqi <= 300:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    def get_color(self, obj):
        aqi = obj.get('aqi', 0)
        if aqi <= 50:
            return '#10b981'
        elif aqi <= 100:
            return '#f59e0b'
        elif aqi <= 150:
            return '#f97316'
        elif aqi <= 200:
            return '#ef4444'
        elif aqi <= 300:
            return '#8b5cf6'
        else:
            return '#7c2d12'


class ForecastSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()
    aqi = serializers.IntegerField()
    pollutant = serializers.CharField(max_length=10)
    confidence = serializers.FloatField()
    category = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    
    def get_category(self, obj):
        return CurrentAQISerializer().get_category(obj)
    
    def get_color(self, obj):
        return CurrentAQISerializer().get_color(obj)