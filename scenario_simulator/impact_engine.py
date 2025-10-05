"""
Impact Engine for Scenario Simulation

This module contains the core simulation logic for calculating air quality
impacts based on different scenarios and environmental factors.
"""

import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from .models import SimulationScenario, SimulationResult, ImpactFactor
from dashboard.models import AirQualityReading
import logging
import math

logger = logging.getLogger(__name__)


def run_scenario_simulation(scenario):
    """
    Run a complete scenario simulation
    
    Args:
        scenario: SimulationScenario object
        
    Returns:
        Boolean indicating success/failure
    """
    try:
        logger.info(f"Starting simulation for scenario: {scenario.name}")
        
        # Clear any existing results
        scenario.result_points.all().delete()
        
        # Get baseline data
        baseline_data = get_baseline_data(scenario.location, scenario.start_date, scenario.end_date)
        
        if not baseline_data:
            logger.warning(f"No baseline data available for {scenario.location}")
            # Generate synthetic baseline data
            baseline_data = generate_synthetic_baseline(scenario)
        
        # Calculate time steps
        time_steps = calculate_time_steps(scenario.start_date, scenario.end_date, scenario.time_resolution)
        total_steps = len(time_steps)
        
        # Process each time step
        results = []
        for i, timestamp in enumerate(time_steps):
            # Update progress
            progress = int((i / total_steps) * 100)
            scenario.progress_percent = progress
            scenario.save()
            
            # Calculate air quality for this timestamp
            result = calculate_timestep_impact(scenario, timestamp, baseline_data)
            
            if result:
                results.append(result)
        
        # Bulk create results
        SimulationResult.objects.bulk_create(results)
        
        # Mark scenario as completed
        scenario.status = 'completed'
        scenario.progress_percent = 100
        scenario.completed_at = timezone.now()
        scenario.save()
        
        logger.info(f"Simulation completed successfully for scenario: {scenario.name}")
        return True
        
    except Exception as e:
        logger.error(f"Simulation failed for scenario {scenario.name}: {e}")
        scenario.status = 'failed'
        scenario.error_message = str(e)
        scenario.save()
        return False


def get_baseline_data(location, start_date, end_date):
    """
    Get baseline air quality data for the specified location and time period
    
    Args:
        location: Location name
        start_date: Start datetime
        end_date: End datetime
        
    Returns:
        Dictionary with baseline air quality data
    """
    try:
        # Get historical data from the same time period in previous year
        baseline_start = start_date - timedelta(days=365)
        baseline_end = end_date - timedelta(days=365)
        
        baseline_readings = AirQualityReading.objects.filter(
            location__icontains=location,
            timestamp__gte=baseline_start,
            timestamp__lte=baseline_end
        ).order_by('timestamp')
        
        if baseline_readings.exists():
            # Calculate average values by pollutant
            baseline_data = {}
            pollutant_types = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
            
            for pollutant in pollutant_types:
                pollutant_readings = baseline_readings.filter(pollutant_type=pollutant)
                if pollutant_readings.exists():
                    avg_concentration = sum(r.concentration for r in pollutant_readings) / len(pollutant_readings)
                    avg_aqi = sum(r.aqi_value for r in pollutant_readings) / len(pollutant_readings)
                    
                    baseline_data[pollutant.lower().replace('.', '')] = {
                        'concentration': avg_concentration,
                        'aqi': avg_aqi
                    }
            
            return baseline_data
            
    except Exception as e:
        logger.error(f"Error getting baseline data for {location}: {e}")
    
    return None


def generate_synthetic_baseline(scenario):
    """
    Generate synthetic baseline data when historical data is not available
    
    Args:
        scenario: SimulationScenario object
        
    Returns:
        Dictionary with synthetic baseline data
    """
    # Typical urban air quality values (moderate conditions)
    baseline_data = {
        'pm25': {'concentration': 25.0, 'aqi': 75},
        'pm10': {'concentration': 45.0, 'aqi': 70},
        'no2': {'concentration': 30.0, 'aqi': 65},
        'so2': {'concentration': 10.0, 'aqi': 40},
        'co': {'concentration': 2.0, 'aqi': 35},
        'o3': {'concentration': 80.0, 'aqi': 85},
    }
    
    # Adjust based on scenario location characteristics
    location_lower = scenario.location.lower()
    
    # Urban areas typically have higher pollution
    if any(urban_term in location_lower for urban_term in ['city', 'downtown', 'urban', 'metro']):
        for pollutant in baseline_data:
            baseline_data[pollutant]['concentration'] *= 1.3
            baseline_data[pollutant]['aqi'] = min(200, baseline_data[pollutant]['aqi'] * 1.2)
    
    # Rural areas typically have lower pollution
    elif any(rural_term in location_lower for rural_term in ['rural', 'country', 'village', 'farm']):
        for pollutant in baseline_data:
            baseline_data[pollutant]['concentration'] *= 0.6
            baseline_data[pollutant]['aqi'] = max(20, baseline_data[pollutant]['aqi'] * 0.7)
    
    return baseline_data


def calculate_time_steps(start_date, end_date, resolution):
    """
    Calculate time steps for the simulation
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        resolution: Time resolution ('hourly', 'daily', 'weekly')
        
    Returns:
        List of datetime objects
    """
    time_steps = []
    current_time = start_date
    
    if resolution == 'hourly':
        delta = timedelta(hours=1)
    elif resolution == 'daily':
        delta = timedelta(days=1)
    elif resolution == 'weekly':
        delta = timedelta(weeks=1)
    else:
        delta = timedelta(hours=1)  # Default to hourly
    
    while current_time <= end_date:
        time_steps.append(current_time)
        current_time += delta
    
    return time_steps


def calculate_timestep_impact(scenario, timestamp, baseline_data):
    """
    Calculate air quality impact for a specific timestamp
    
    Args:
        scenario: SimulationScenario object
        timestamp: Datetime for this calculation
        baseline_data: Baseline air quality data
        
    Returns:
        SimulationResult object
    """
    try:
        # Start with baseline values
        pollutant_concentrations = {}
        baseline_aqi_values = {}
        
        for pollutant in ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3']:
            if pollutant in baseline_data:
                pollutant_concentrations[pollutant] = baseline_data[pollutant]['concentration']
                baseline_aqi_values[pollutant] = baseline_data[pollutant]['aqi']
            else:
                # Default values if not available
                defaults = {
                    'pm25': 25.0, 'pm10': 45.0, 'no2': 30.0,
                    'so2': 10.0, 'co': 2.0, 'o3': 80.0
                }
                pollutant_concentrations[pollutant] = defaults.get(pollutant, 25.0)
                baseline_aqi_values[pollutant] = 75
        
        # Apply scenario impacts
        impact_factors = get_applicable_impact_factors(scenario, timestamp)
        
        for factor in impact_factors:
            # Apply factor coefficients to concentrations
            for pollutant in pollutant_concentrations:
                coefficient_attr = f"{pollutant}_coefficient"
                if hasattr(factor, coefficient_attr):
                    coefficient = getattr(factor, coefficient_attr)
                    
                    # Get intensity from scenario parameters
                    intensity = get_factor_intensity(scenario, factor, timestamp)
                    
                    # Apply impact
                    pollutant_concentrations[pollutant] *= (1 + (coefficient - 1) * intensity)
        
        # Apply temporal variations
        pollutant_concentrations = apply_temporal_variations(pollutant_concentrations, timestamp)
        
        # Apply weather effects
        pollutant_concentrations = apply_weather_effects(pollutant_concentrations, scenario, timestamp)
        
        # Calculate final AQI values
        aqi_values = {}
        for pollutant, concentration in pollutant_concentrations.items():
            aqi_values[pollutant] = calculate_aqi_from_concentration(concentration, pollutant)
        
        # Use the highest AQI as the overall AQI (US EPA method)
        overall_aqi = max(aqi_values.values())
        baseline_overall_aqi = max(baseline_aqi_values.values())
        
        # Calculate improvement percentage
        improvement_percent = ((baseline_overall_aqi - overall_aqi) / baseline_overall_aqi) * 100
        
        # Create result object
        result = SimulationResult(
            scenario=scenario,
            timestamp=timestamp,
            pm25_concentration=pollutant_concentrations['pm25'],
            pm10_concentration=pollutant_concentrations['pm10'],
            no2_concentration=pollutant_concentrations['no2'],
            so2_concentration=pollutant_concentrations['so2'],
            co_concentration=pollutant_concentrations['co'],
            o3_concentration=pollutant_concentrations['o3'],
            aqi_value=int(overall_aqi),
            baseline_aqi=int(baseline_overall_aqi),
            improvement_percent=improvement_percent,
            visibility_km=calculate_visibility(pollutant_concentrations),
            health_risk_index=calculate_health_risk(overall_aqi)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating timestep impact: {e}")
        return None


def get_applicable_impact_factors(scenario, timestamp):
    """Get impact factors applicable to the scenario and timestamp"""
    factors = []
    
    # Get factors based on scenario parameters
    for param_name, param_value in scenario.parameters.items():
        if param_value > 0:  # Only consider active factors
            # Try to find matching impact factors
            matching_factors = ImpactFactor.objects.filter(
                name__icontains=param_name,
                is_active=True
            )
            factors.extend(matching_factors)
    
    # Get scenario-type specific factors
    if scenario.template:
        template_factors = ImpactFactor.objects.filter(
            factor_type=scenario.template.scenario_type,
            is_active=True
        )
        factors.extend(template_factors)
    
    return factors


def get_factor_intensity(scenario, factor, timestamp):
    """
    Calculate the intensity of an impact factor for a given timestamp
    
    Args:
        scenario: SimulationScenario object
        factor: ImpactFactor object
        timestamp: Current timestamp
        
    Returns:
        Float intensity value (0.0 to 1.0)
    """
    # Base intensity from scenario parameters
    factor_name_lower = factor.name.lower().replace(' ', '_')
    base_intensity = 0.5  # Default moderate intensity
    
    # Look for matching parameter in scenario
    for param_name, param_value in scenario.parameters.items():
        if factor_name_lower in param_name.lower():
            try:
                base_intensity = float(param_value) / 100.0  # Assume parameters are in percentage
                base_intensity = max(0.0, min(1.0, base_intensity))  # Clamp to 0-1
            except (ValueError, TypeError):
                pass
            break
    
    # Apply temporal variations
    hour = timestamp.hour
    day_of_week = timestamp.weekday()
    month = timestamp.month
    
    # Traffic factors are higher during rush hours and weekdays
    if factor.factor_type == 'transportation':
        if hour in [7, 8, 9, 17, 18, 19]:  # Rush hours
            base_intensity *= 1.3
        elif day_of_week >= 5:  # Weekend
            base_intensity *= 0.7
    
    # Industrial factors might be lower at night and weekends
    elif factor.factor_type == 'industrial':
        if hour < 6 or hour > 22:  # Night hours
            base_intensity *= 0.6
        elif day_of_week >= 5:  # Weekend
            base_intensity *= 0.5
    
    # Wildfire factors might be seasonal
    elif factor.factor_type == 'natural' and 'fire' in factor.name.lower():
        if month in [6, 7, 8, 9]:  # Fire season
            base_intensity *= factor.seasonal_factor
        else:
            base_intensity *= 0.3
    
    return min(1.0, base_intensity)


def apply_temporal_variations(concentrations, timestamp):
    """Apply daily and seasonal temporal variations to concentrations"""
    hour = timestamp.hour
    month = timestamp.month
    
    # Daily variations (simplified)
    daily_factor = 1.0 + 0.3 * math.sin((hour - 6) * math.pi / 12)  # Peak around noon
    
    # Seasonal variations (simplified)
    seasonal_factor = 1.0 + 0.2 * math.sin((month - 3) * math.pi / 6)  # Peak in summer
    
    # Apply variations
    for pollutant in concentrations:
        concentrations[pollutant] *= daily_factor * seasonal_factor
    
    return concentrations


def apply_weather_effects(concentrations, scenario, timestamp):
    """Apply weather effects to pollutant concentrations"""
    # Get weather parameters from scenario (if available)
    weather_params = scenario.parameters.get('weather', {})
    
    # Wind speed effect (higher wind speed reduces concentrations)
    wind_speed = weather_params.get('wind_speed', 5.0)  # m/s, default moderate
    wind_factor = 1.0 / (1.0 + wind_speed / 10.0)
    
    # Temperature effect (higher temperature can increase some pollutants)
    temperature = weather_params.get('temperature', 20.0)  # Celsius, default moderate
    temp_factor = 1.0 + (temperature - 20.0) / 100.0
    
    # Humidity effect (high humidity can affect particle concentrations)
    humidity = weather_params.get('humidity', 50.0)  # %, default moderate
    humidity_factor = 1.0 + (humidity - 50.0) / 200.0
    
    # Apply weather effects
    for pollutant in concentrations:
        concentrations[pollutant] *= wind_factor * temp_factor
        
        # Humidity mainly affects particulate matter
        if pollutant in ['pm25', 'pm10']:
            concentrations[pollutant] *= humidity_factor
    
    return concentrations


def calculate_aqi_from_concentration(concentration, pollutant_type):
    """
    Convert pollutant concentration to AQI value
    
    Args:
        concentration: Pollutant concentration
        pollutant_type: Type of pollutant
        
    Returns:
        AQI value
    """
    # Simplified AQI calculation (US EPA breakpoints)
    if pollutant_type == 'pm25':
        if concentration <= 12.0:
            return (50 / 12.0) * concentration
        elif concentration <= 35.4:
            return 50 + ((100 - 50) / (35.4 - 12.1)) * (concentration - 12.1)
        elif concentration <= 55.4:
            return 100 + ((150 - 100) / (55.4 - 35.5)) * (concentration - 35.5)
        else:
            return min(500, 150 + ((200 - 150) / (150.4 - 55.5)) * (concentration - 55.5))
    
    elif pollutant_type == 'pm10':
        if concentration <= 54:
            return (50 / 54) * concentration
        elif concentration <= 154:
            return 50 + ((100 - 50) / (154 - 55)) * (concentration - 55)
        else:
            return min(500, 100 + ((150 - 100) / (254 - 155)) * (concentration - 155))
    
    else:
        # Generic calculation for other pollutants
        return min(500, max(0, concentration * 2))


def calculate_visibility(concentrations):
    """Calculate visibility based on pollutant concentrations"""
    pm25 = concentrations.get('pm25', 0)
    pm10 = concentrations.get('pm10', 0)
    
    # Simplified visibility calculation (empirical formula)
    visibility = 40.0 / (1.0 + (pm25 + pm10) / 50.0)
    return max(1.0, min(40.0, visibility))  # Clamp between 1-40 km


def calculate_health_risk(aqi_value):
    """Calculate health risk index based on AQI"""
    if aqi_value <= 50:
        return 0.1  # Low risk
    elif aqi_value <= 100:
        return 0.3  # Moderate risk
    elif aqi_value <= 150:
        return 0.6  # High risk for sensitive groups
    elif aqi_value <= 200:
        return 0.8  # Unhealthy
    else:
        return 1.0  # Very unhealthy/hazardous


def validate_scenario_parameters(scenario):
    """
    Validate scenario parameters before running simulation
    
    Args:
        scenario: SimulationScenario object
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check date range
    if scenario.start_date >= scenario.end_date:
        errors.append("End date must be after start date")
    
    # Check simulation duration (limit to reasonable range)
    duration = scenario.end_date - scenario.start_date
    if duration.days > 365:
        errors.append("Simulation duration cannot exceed 365 days")
    
    # Check location coordinates
    if not (-90 <= scenario.latitude <= 90):
        errors.append("Latitude must be between -90 and 90 degrees")
    
    if not (-180 <= scenario.longitude <= 180):
        errors.append("Longitude must be between -180 and 180 degrees")
    
    # Check parameters
    if not scenario.parameters:
        errors.append("At least one impact parameter must be specified")
    
    return len(errors) == 0, errors