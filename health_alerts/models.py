from django.db import models
from django.contrib.auth.models import User
from dashboard.models import AirQualityReading


class HealthCondition(models.Model):
    """Health conditions that can be affected by air quality"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    aqi_threshold = models.IntegerField(default=100)  # Default alert threshold
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserHealthProfile(models.Model):
    """User health profile for personalized alerts"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(blank=True, null=True)
    conditions = models.ManyToManyField(HealthCondition, blank=True)
    custom_threshold = models.IntegerField(default=100)  # Custom AQI threshold
    alert_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
        ],
        default='immediate'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Health Profile"


class Alert(models.Model):
    """Health alert instances"""
    ALERT_TYPES = [
        ('aqi_threshold', 'AQI Threshold Exceeded'),
        ('health_warning', 'Health Warning'),
        ('forecast_alert', 'Forecast Alert'),
        ('emergency', 'Emergency Alert'),
    ]

    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    location = models.CharField(max_length=100)
    aqi_value = models.IntegerField(blank=True, null=True)
    pollutant = models.CharField(max_length=20, blank=True)
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    sent_via_push = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class AlertTemplate(models.Model):
    """Templates for different types of alerts"""
    alert_type = models.CharField(max_length=20, unique=True)
    title_template = models.CharField(max_length=200)
    message_template = models.TextField()
    default_severity = models.CharField(max_length=10, default='medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Template: {self.alert_type}"