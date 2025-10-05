from django.contrib import admin
from .models import AirQualityReading, UserLocationPreference, MLPrediction


@admin.register(AirQualityReading)
class AirQualityReadingAdmin(admin.ModelAdmin):
    list_display = ('location', 'aqi_value', 'pollutant_type', 'timestamp')
    list_filter = ('pollutant_type', 'timestamp', 'location')
    search_fields = ('location', 'pollutant_type')
    ordering = ('-timestamp',)


@admin.register(UserLocationPreference)
class UserLocationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'location_name', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('user__username', 'location_name')


@admin.register(MLPrediction)
class MLPredictionAdmin(admin.ModelAdmin):
    list_display = ('location', 'predicted_aqi', 'pollutant_type', 'prediction_for', 'confidence_score')
    list_filter = ('pollutant_type', 'prediction_for', 'created_at')
    search_fields = ('location', 'pollutant_type')
    ordering = ('-prediction_for',)