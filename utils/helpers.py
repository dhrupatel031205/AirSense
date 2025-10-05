"""
Helper functions and utilities for the air quality project
"""

from datetime import datetime, timedelta
from django.utils import timezone
import re
import hashlib
import random
import string


def validate_coordinates(latitude, longitude):
    """
    Validate latitude and longitude coordinates
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90 degrees"
        
        if not (-180 <= lng <= 180):
            return False, "Longitude must be between -180 and 180 degrees"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"


def validate_aqi_value(aqi_value):
    """
    Validate AQI value
    
    Args:
        aqi_value: AQI value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        aqi = int(aqi_value)
        
        if aqi < 0:
            return False, "AQI value cannot be negative"
        
        if aqi > 500:
            return False, "AQI value cannot exceed 500"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, "AQI value must be a number"


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    import math
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Earth's radius in kilometers
    
    return c * r


def format_duration(seconds):
    """
    Format duration in seconds to human readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''}"


def generate_random_string(length=8):
    """
    Generate a random string of specified length
    
    Args:
        length: Length of the string to generate
        
    Returns:
        Random string
    """
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def sanitize_filename(filename):
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove any characters that aren't alphanumeric, hyphens, underscores, or dots
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple consecutive underscores
    filename = re.sub(r'_{2,}', '_', filename)
    
    # Ensure the filename isn't too long
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename


def hash_string(input_string):
    """
    Generate SHA-256 hash of a string
    
    Args:
        input_string: String to hash
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


def parse_pollutant_concentration(concentration_str, pollutant_type):
    """
    Parse pollutant concentration string and convert to standard units
    
    Args:
        concentration_str: Concentration string (e.g., "25.5 μg/m³")
        pollutant_type: Type of pollutant
        
    Returns:
        Float concentration value in standard units
    """
    try:
        # Extract numeric value
        numeric_match = re.search(r'[\d.]+', str(concentration_str))
        if not numeric_match:
            return None
        
        value = float(numeric_match.group())
        
        # Convert units if necessary
        concentration_lower = str(concentration_str).lower()
        
        if 'mg/m³' in concentration_lower or 'mg/m3' in concentration_lower:
            # Convert mg/m³ to μg/m³
            value *= 1000
        elif 'ppm' in concentration_lower:
            # Convert ppm to μg/m³ (approximate conversion)
            if pollutant_type == 'CO':
                value *= 1150  # CO: 1 ppm ≈ 1150 μg/m³
            elif pollutant_type == 'NO2':
                value *= 1880  # NO2: 1 ppm ≈ 1880 μg/m³
            elif pollutant_type == 'SO2':
                value *= 2620  # SO2: 1 ppm ≈ 2620 μg/m³
        
        return value
        
    except (ValueError, AttributeError):
        return None


def get_aqi_breakpoints():
    """
    Get AQI breakpoints for different pollutants (US EPA standards)
    
    Returns:
        Dictionary with AQI breakpoints
    """
    return {
        'PM2.5': [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 350.4, 301, 400),
            (350.5, 500.4, 401, 500)
        ],
        'PM10': [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 504, 301, 400),
            (505, 604, 401, 500)
        ],
        'NO2': [
            (0, 53, 0, 50),
            (54, 100, 51, 100),
            (101, 360, 101, 150),
            (361, 649, 151, 200),
            (650, 1249, 201, 300),
            (1250, 1649, 301, 400),
            (1650, 2049, 401, 500)
        ]
    }


def calculate_aqi_from_concentration(concentration, pollutant_type):
    """
    Calculate AQI from pollutant concentration using EPA breakpoints
    
    Args:
        concentration: Pollutant concentration
        pollutant_type: Type of pollutant
        
    Returns:
        AQI value
    """
    breakpoints = get_aqi_breakpoints()
    
    if pollutant_type not in breakpoints:
        # Default calculation for unknown pollutants
        return min(500, max(0, int(concentration * 2)))
    
    pollutant_breakpoints = breakpoints[pollutant_type]
    
    for bp_low_conc, bp_high_conc, bp_low_aqi, bp_high_aqi in pollutant_breakpoints:
        if bp_low_conc <= concentration <= bp_high_conc:
            # Linear interpolation within the breakpoint range
            aqi = ((bp_high_aqi - bp_low_aqi) / (bp_high_conc - bp_low_conc)) * (concentration - bp_low_conc) + bp_low_aqi
            return int(round(aqi))
    
    # If concentration is above the highest breakpoint
    return 500


def get_recent_timestamp_ranges():
    """
    Get common timestamp ranges for filtering
    
    Returns:
        Dictionary with timestamp ranges
    """
    now = timezone.now()
    
    return {
        'last_hour': now - timedelta(hours=1),
        'last_6_hours': now - timedelta(hours=6),
        'last_24_hours': now - timedelta(hours=24),
        'last_week': now - timedelta(days=7),
        'last_month': now - timedelta(days=30),
        'last_year': now - timedelta(days=365),
    }


def validate_email(email):
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Boolean indicating if email is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_large_number(number):
    """
    Format large numbers with appropriate suffixes (K, M, B)
    
    Args:
        number: Number to format
        
    Returns:
        Formatted string
    """
    try:
        num = float(number)
        
        if abs(num) >= 1000000000:
            return f"{num/1000000000:.1f}B"
        elif abs(num) >= 1000000:
            return f"{num/1000000:.1f}M"
        elif abs(num) >= 1000:
            return f"{num/1000:.1f}K"
        else:
            return str(int(num))
            
    except (ValueError, TypeError):
        return str(number)


def get_season_from_date(date):
    """
    Get season from date
    
    Args:
        date: Date object
        
    Returns:
        Season name
    """
    month = date.month
    
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'


def calculate_air_quality_trend(readings):
    """
    Calculate trend from a series of air quality readings
    
    Args:
        readings: List of AQI values
        
    Returns:
        Tuple of (trend_direction, trend_percentage)
    """
    if len(readings) < 2:
        return 'stable', 0
    
    # Simple linear regression to determine trend
    n = len(readings)
    x = list(range(n))
    y = readings
    
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return 'stable', 0
    
    slope = numerator / denominator
    
    # Calculate percentage change
    if y_mean != 0:
        trend_percentage = (slope * (n - 1) / y_mean) * 100
    else:
        trend_percentage = 0
    
    if abs(trend_percentage) < 5:
        return 'stable', trend_percentage
    elif trend_percentage > 0:
        return 'increasing', trend_percentage
    else:
        return 'decreasing', abs(trend_percentage)


def safe_division(numerator, denominator, default=0):
    """
    Safely divide two numbers, returning default if division by zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value to return if division by zero
        
    Returns:
        Division result or default value
    """
    try:
        return float(numerator) / float(denominator)
    except (ValueError, TypeError, ZeroDivisionError):
        return default


class LocationUtils:
    """Utility class for location-related functions"""
    
    @staticmethod
    def get_location_type(location_name):
        """
        Determine location type based on name
        
        Args:
            location_name: Name of the location
            
        Returns:
            Location type string
        """
        name_lower = location_name.lower()
        
        if any(urban_term in name_lower for urban_term in ['city', 'downtown', 'urban', 'metro']):
            return 'urban'
        elif any(suburb_term in name_lower for suburb_term in ['suburb', 'residential']):
            return 'suburban'
        elif any(rural_term in name_lower for rural_term in ['rural', 'country', 'village', 'farm']):
            return 'rural'
        elif any(industrial_term in name_lower for industrial_term in ['industrial', 'factory', 'port']):
            return 'industrial'
        else:
            return 'mixed'
    
    @staticmethod
    def format_coordinates_dms(latitude, longitude):
        """
        Format coordinates in degrees, minutes, seconds format
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Formatted DMS string
        """
        def decimal_to_dms(decimal_degrees):
            degrees = int(decimal_degrees)
            minutes_float = abs(decimal_degrees - degrees) * 60
            minutes = int(minutes_float)
            seconds = (minutes_float - minutes) * 60
            return degrees, minutes, seconds
        
        try:
            lat = float(latitude)
            lng = float(longitude)
            
            lat_deg, lat_min, lat_sec = decimal_to_dms(abs(lat))
            lng_deg, lng_min, lng_sec = decimal_to_dms(abs(lng))
            
            lat_dir = 'N' if lat >= 0 else 'S'
            lng_dir = 'E' if lng >= 0 else 'W'
            
            return f"{lat_deg}°{lat_min}'{lat_sec:.1f}\"{lat_dir} {lng_deg}°{lng_min}'{lng_sec:.1f}\"{lng_dir}"
            
        except (ValueError, TypeError):
            return "Invalid coordinates"