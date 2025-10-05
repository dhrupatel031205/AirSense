"""
API clients for external services (NASA TEMPO, weather APIs, etc.)
"""

import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class NASATempoClient:
    """Client for NASA TEMPO API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'NASA_API_KEY', '')
        self.base_url = 'https://api.nasa.gov/tempo'
        self.session = requests.Session()
        
    def get_air_quality_data(self, latitude, longitude, start_date=None, end_date=None):
        """
        Get air quality data from NASA TEMPO
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_date: Start date for data (optional)
            end_date: End date for data (optional)
            
        Returns:
            Dictionary with air quality data
        """
        try:
            cache_key = f"nasa_tempo_{latitude}_{longitude}_{start_date}_{end_date}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # Prepare parameters
            params = {
                'api_key': self.api_key,
                'lat': latitude,
                'lon': longitude,
            }
            
            if start_date:
                params['start_date'] = start_date.strftime('%Y-%m-%d')
            if end_date:
                params['end_date'] = end_date.strftime('%Y-%m-%d')
            
            # Make API request
            response = self.session.get(f"{self.base_url}/data", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform data to our format
            transformed_data = self._transform_tempo_data(data)
            
            # Cache the result for 1 hour
            cache.set(cache_key, transformed_data, 3600)
            
            return transformed_data
            
        except requests.RequestException as e:
            logger.error(f"NASA TEMPO API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing NASA TEMPO data: {e}")
            return None
    
    def _transform_tempo_data(self, raw_data):
        """Transform NASA TEMPO data to our format"""
        # This is a placeholder transformation
        # In reality, you'd parse the specific NASA TEMPO data format
        
        if not raw_data or 'data' not in raw_data:
            return None
        
        transformed = []
        
        for record in raw_data.get('data', []):
            transformed_record = {
                'timestamp': record.get('time'),
                'latitude': record.get('lat'),
                'longitude': record.get('lon'),
                'pollutants': {}
            }
            
            # Map NASA pollutant names to our format
            pollutant_mapping = {
                'no2': 'NO2',
                'o3': 'O3',
                'so2': 'SO2',
                'co': 'CO'
            }
            
            for nasa_name, our_name in pollutant_mapping.items():
                if nasa_name in record:
                    transformed_record['pollutants'][our_name] = {
                        'concentration': record[nasa_name].get('value'),
                        'unit': record[nasa_name].get('unit', 'μg/m³')
                    }
            
            transformed.append(transformed_record)
        
        return transformed


class WeatherAPIClient:
    """Client for weather data APIs"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'WEATHER_API_KEY', '')
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        self.session = requests.Session()
    
    def get_current_weather(self, latitude, longitude):
        """
        Get current weather data
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with weather data
        """
        try:
            cache_key = f"weather_current_{latitude}_{longitude}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = self.session.get(f"{self.base_url}/weather", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            transformed_data = self._transform_current_weather(data)
            
            # Cache for 30 minutes
            cache.set(cache_key, transformed_data, 1800)
            
            return transformed_data
            
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return None
    
    def get_weather_forecast(self, latitude, longitude, days=5):
        """
        Get weather forecast
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days to forecast
            
        Returns:
            List of forecast data
        """
        try:
            cache_key = f"weather_forecast_{latitude}_{longitude}_{days}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = self.session.get(f"{self.base_url}/forecast", params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            transformed_data = self._transform_forecast_data(data)
            
            # Cache for 1 hour
            cache.set(cache_key, transformed_data, 3600)
            
            return transformed_data
            
        except requests.RequestException as e:
            logger.error(f"Weather forecast API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing forecast data: {e}")
            return None
    
    def _transform_current_weather(self, raw_data):
        """Transform current weather data to our format"""
        if not raw_data:
            return None
        
        return {
            'temperature': raw_data.get('main', {}).get('temp'),
            'humidity': raw_data.get('main', {}).get('humidity'),
            'pressure': raw_data.get('main', {}).get('pressure'),
            'wind_speed': raw_data.get('wind', {}).get('speed'),
            'wind_direction': raw_data.get('wind', {}).get('deg'),
            'weather_condition': raw_data.get('weather', [{}])[0].get('main'),
            'weather_description': raw_data.get('weather', [{}])[0].get('description'),
            'visibility': raw_data.get('visibility'),
            'timestamp': datetime.utcfromtimestamp(raw_data.get('dt', 0))
        }
    
    def _transform_forecast_data(self, raw_data):
        """Transform forecast data to our format"""
        if not raw_data or 'list' not in raw_data:
            return []
        
        forecast_list = []
        
        for item in raw_data['list']:
            forecast_item = {
                'timestamp': datetime.utcfromtimestamp(item.get('dt', 0)),
                'temperature': item.get('main', {}).get('temp'),
                'humidity': item.get('main', {}).get('humidity'),
                'pressure': item.get('main', {}).get('pressure'),
                'wind_speed': item.get('wind', {}).get('speed'),
                'wind_direction': item.get('wind', {}).get('deg'),
                'weather_condition': item.get('weather', [{}])[0].get('main'),
                'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
            }
            forecast_list.append(forecast_item)
        
        return forecast_list


class AirQualityAPIClient:
    """Client for generic air quality APIs"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_waqi_data(self, latitude, longitude):
        """
        Get data from World Air Quality Index API
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with air quality data
        """
        try:
            cache_key = f"waqi_{latitude}_{longitude}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return cached_data
            
            # WAQI API endpoint (requires API token)
            url = f"https://api.waqi.info/feed/geo:{latitude};{longitude}/"
            
            params = {
                'token': getattr(settings, 'WAQI_API_TOKEN', '')
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                transformed_data = self._transform_waqi_data(data.get('data', {}))
                
                # Cache for 1 hour
                cache.set(cache_key, transformed_data, 3600)
                
                return transformed_data
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"WAQI API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing WAQI data: {e}")
            return None
    
    def _transform_waqi_data(self, raw_data):
        """Transform WAQI data to our format"""
        if not raw_data:
            return None
        
        # Extract pollutant data
        iaqi = raw_data.get('iaqi', {})
        pollutants = {}
        
        pollutant_mapping = {
            'pm25': 'PM2.5',
            'pm10': 'PM10',
            'no2': 'NO2',
            'so2': 'SO2',
            'co': 'CO',
            'o3': 'O3'
        }
        
        for waqi_name, our_name in pollutant_mapping.items():
            if waqi_name in iaqi:
                pollutants[our_name] = {
                    'aqi': iaqi[waqi_name].get('v'),
                    'concentration': None  # WAQI doesn't always provide concentrations
                }
        
        return {
            'station_name': raw_data.get('city', {}).get('name'),
            'aqi': raw_data.get('aqi'),
            'pollutants': pollutants,
            'timestamp': raw_data.get('time', {}).get('iso'),
            'latitude': raw_data.get('city', {}).get('geo', [None])[0],
            'longitude': raw_data.get('city', {}).get('geo', [None])[1]
        }


def fetch_current_air_quality(latitude, longitude):
    """
    Fetch current air quality data from available APIs
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with consolidated air quality data
    """
    # Try multiple data sources
    data_sources = []
    
    # Try NASA TEMPO
    nasa_client = NASATempoClient()
    nasa_data = nasa_client.get_air_quality_data(latitude, longitude)
    if nasa_data:
        data_sources.append(('NASA TEMPO', nasa_data))
    
    # Try WAQI
    waqi_client = AirQualityAPIClient()
    waqi_data = waqi_client.get_waqi_data(latitude, longitude)
    if waqi_data:
        data_sources.append(('WAQI', waqi_data))
    
    # Consolidate data from multiple sources
    if not data_sources:
        return None
    
    # Use the first available source for now
    # In a real implementation, you might want to merge/average multiple sources
    source_name, data = data_sources[0]
    
    return {
        'source': source_name,
        'data': data,
        'fetched_at': datetime.now()
    }


def fetch_weather_data(latitude, longitude):
    """
    Fetch weather data for a location
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        Dictionary with weather data
    """
    weather_client = WeatherAPIClient()
    
    current_weather = weather_client.get_current_weather(latitude, longitude)
    forecast = weather_client.get_weather_forecast(latitude, longitude, days=3)
    
    return {
        'current': current_weather,
        'forecast': forecast
    }


class APIRateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.call_times = []
    
    def can_make_call(self):
        """Check if we can make an API call without exceeding rate limits"""
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Remove old call times
        self.call_times = [call_time for call_time in self.call_times if call_time > one_minute_ago]
        
        # Check if we're under the limit
        if len(self.call_times) < self.calls_per_minute:
            self.call_times.append(now)
            return True
        
        return False
    
    def time_until_next_call(self):
        """Get time until next call can be made"""
        if not self.call_times:
            return 0
        
        oldest_call = min(self.call_times)
        time_until_reset = (oldest_call + timedelta(minutes=1)) - datetime.now()
        
        return max(0, time_until_reset.total_seconds())


# Global rate limiters for different APIs
nasa_rate_limiter = APIRateLimiter(calls_per_minute=100)
weather_rate_limiter = APIRateLimiter(calls_per_minute=60)
waqi_rate_limiter = APIRateLimiter(calls_per_minute=1000)