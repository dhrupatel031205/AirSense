from django.db import models
from django.contrib.auth.models import User


class AirQualityReading(models.Model):
    POLLUTANT_CHOICES = [
        ('PM2.5', 'PM2.5'),
        ('PM10', 'PM10'),
        ('NO2', 'Nitrogen Dioxide'),
        ('SO2', 'Sulfur Dioxide'),
        ('CO', 'Carbon Monoxide'),
        ('O3', 'Ozone'),
    ]

    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pollutant_type = models.CharField(max_length=10, choices=POLLUTANT_CHOICES)
    concentration = models.FloatField()  # μg/m³ or ppm
    aqi_value = models.IntegerField()  # Air Quality Index
    timestamp = models.DateTimeField()
    source = models.CharField(max_length=50)  # NASA TEMPO, local sensor, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['location', '-timestamp']),
            models.Index(fields=['pollutant_type', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.location} - {self.pollutant_type}: {self.concentration} ({self.timestamp})"


class UserLocationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_primary = models.BooleanField(default=False)
    alert_threshold = models.IntegerField(default=100)  # AQI threshold for alerts
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'location_name']

    def __str__(self):
        return f"{self.user.username} - {self.location_name}"


class MLPrediction(models.Model):
    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    pollutant_type = models.CharField(max_length=10, choices=AirQualityReading.POLLUTANT_CHOICES)
    predicted_concentration = models.FloatField()
    predicted_aqi = models.IntegerField()
    confidence_score = models.FloatField()  # 0.0 to 1.0
    prediction_horizon_hours = models.IntegerField()  # How many hours ahead
    model_type = models.CharField(max_length=20)  # CNN, LSTM, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    prediction_for = models.DateTimeField()  # The time this prediction is for

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction for {self.location} - {self.pollutant_type} at {self.prediction_for}"