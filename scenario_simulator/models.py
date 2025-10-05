from django.db import models
from django.contrib.auth.models import User


class ScenarioTemplate(models.Model):
    """Predefined scenario templates"""
    SCENARIO_TYPES = [
        ('wildfire', 'Wildfire Impact'),
        ('traffic', 'Traffic Reduction'),
        ('industrial', 'Industrial Changes'),
        ('weather', 'Weather Pattern Changes'),
        ('policy', 'Policy Implementation'),
        ('seasonal', 'Seasonal Variations'),
        ('custom', 'Custom Scenario'),
    ]

    COMPLEXITY_CHOICES = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),  # 12 characters
        ('advanced', 'Advanced'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_TYPES)
    default_parameters = models.JSONField(default=dict)  # Default simulation parameters
    complexity_level = models.CharField(
        max_length=12,  # updated to fit longest choice
        choices=COMPLEXITY_CHOICES,
        default='basic'
    )
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SimulationScenario(models.Model):
    """Individual simulation scenarios created by users"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    TIME_RESOLUTION_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.ForeignKey(ScenarioTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    parameters = models.JSONField(default=dict)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    time_resolution = models.CharField(max_length=10, choices=TIME_RESOLUTION_CHOICES, default='hourly')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    progress_percent = models.IntegerField(default=0)
    results = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    @property
    def duration_hours(self):
        """Calculate simulation duration in hours"""
        delta = self.end_date - self.start_date
        return int(delta.total_seconds() / 3600)


class SimulationResult(models.Model):
    """Individual result points from a simulation"""
    scenario = models.ForeignKey(SimulationScenario, on_delete=models.CASCADE, related_name='result_points')
    timestamp = models.DateTimeField()
    pm25_concentration = models.FloatField(null=True, blank=True)
    pm10_concentration = models.FloatField(null=True, blank=True)
    no2_concentration = models.FloatField(null=True, blank=True)
    so2_concentration = models.FloatField(null=True, blank=True)
    co_concentration = models.FloatField(null=True, blank=True)
    o3_concentration = models.FloatField(null=True, blank=True)
    aqi_value = models.IntegerField()
    visibility_km = models.FloatField(null=True, blank=True)
    health_risk_index = models.FloatField(null=True, blank=True)
    baseline_aqi = models.IntegerField(null=True, blank=True)
    improvement_percent = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['scenario', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.scenario.name} - {self.timestamp} (AQI: {self.aqi_value})"


class ScenarioComparison(models.Model):
    """Comparison between multiple scenarios"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scenarios = models.ManyToManyField(SimulationScenario)
    comparison_results = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comparison: {self.name} - {self.user.username}"


class ImpactFactor(models.Model):
    """Factors that can impact air quality in simulations"""
    FACTOR_TYPES = [
        ('emission_source', 'Emission Source'),
        ('weather_pattern', 'Weather Pattern'),
        ('transportation', 'Transportation'),
        ('industrial', 'Industrial Activity'),
        ('natural', 'Natural Event'),
        ('policy', 'Policy Intervention'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    factor_type = models.CharField(max_length=20, choices=FACTOR_TYPES)
    pm25_coefficient = models.FloatField(default=1.0)
    pm10_coefficient = models.FloatField(default=1.0)
    no2_coefficient = models.FloatField(default=1.0)
    so2_coefficient = models.FloatField(default=1.0)
    co_coefficient = models.FloatField(default=1.0)
    o3_coefficient = models.FloatField(default=1.0)
    applicable_regions = models.JSONField(default=list, blank=True)
    seasonal_factor = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.factor_type})"
