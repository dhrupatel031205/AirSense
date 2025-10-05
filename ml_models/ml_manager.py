import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .forecasting import AQIForecaster, SpatialInterpolator
from .anomaly_detection import AQIAnomalyDetector, PersonalizedAlerts
from .scenario_simulator import ScenarioSimulator, PolicyImpactModeler
from .health_recommender import HealthRecommender, HealthChatbot
from .data_validator import CrowdsourcedDataValidator, DataQualityMetrics

class MLModelManager:
    """Central manager for all ML models and predictions"""
    
    def __init__(self):
        self.forecaster = AQIForecaster()
        self.spatial_interpolator = SpatialInterpolator()
        self.anomaly_detector = AQIAnomalyDetector()
        self.personalized_alerts = PersonalizedAlerts()
        self.scenario_simulator = ScenarioSimulator()
        self.policy_modeler = PolicyImpactModeler()
        self.health_recommender = HealthRecommender()
        self.health_chatbot = HealthChatbot()
        self.data_validator = CrowdsourcedDataValidator()
        self.quality_metrics = DataQualityMetrics()
        
        self.models_trained = {
            'forecaster': False,
            'anomaly_detector': False,
            'scenario_simulator': False
        }
    
    def initialize_models(self, historical_data):
        """Initialize and train all models with historical data"""
        try:
            # Train forecasting model
            if len(historical_data) > 100:
                self.forecaster.train(historical_data)
                self.models_trained['forecaster'] = True
            
            # Train anomaly detection
            if len(historical_data) > 50:
                self.anomaly_detector.train(historical_data)
                self.models_trained['anomaly_detector'] = True
            
            # Train scenario simulator
            if len(historical_data) > 100:
                self.scenario_simulator.train(historical_data)
                self.models_trained['scenario_simulator'] = True
            
            return {'success': True, 'models_trained': self.models_trained}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_real_time_predictions(self, location_data, user_profile=None):
        """Get comprehensive real-time predictions for a location"""
        results = {
            'timestamp': datetime.now(),
            'location': location_data.get('location', 'Unknown'),
            'current_aqi': location_data.get('aqi', 50)
        }
        
        # Hourly forecasts
        if self.models_trained['forecaster']:
            results['hourly_forecast'] = self.forecaster.forecast_hourly(location_data, hours=24)
        
        # Anomaly detection
        if self.models_trained['anomaly_detector']:
            current_data = pd.DataFrame([{
                'timestamp': datetime.now(),
                'aqi': location_data.get('aqi', 50),
                'pm25': location_data.get('pm25', 0),
                'pm10': location_data.get('pm10', 0),
                'no2': location_data.get('no2', 0),
                'o3': location_data.get('o3', 0)
            }])
            
            anomaly_results = self.anomaly_detector.detect_anomalies(current_data)
            if anomaly_results:
                results['anomaly_status'] = anomaly_results[0]
                alert = self.anomaly_detector.generate_alert(
                    anomaly_results[0], 
                    location_data.get('location', 'Unknown')
                )
                if alert:
                    results['alert'] = alert
        
        # Health recommendations
        if user_profile:
            results['health_recommendations'] = self.health_recommender.get_recommendations(
                location_data.get('aqi', 50),
                user_profile,
                location_data
            )
            
            # Personalized alerts
            alert_check = self.personalized_alerts.should_alert(
                location_data.get('aqi', 50),
                user_profile
            )
            if alert_check['alert']:
                results['personalized_alert'] = alert_check
        
        return results
    
    def run_scenario_analysis(self, base_data, scenarios=None):
        """Run what-if scenario analysis"""
        if not self.models_trained['scenario_simulator']:
            return {'error': 'Scenario simulator not trained'}
        
        if scenarios:
            results = {}
            for scenario_name, params in scenarios.items():
                results[scenario_name] = self.scenario_simulator.simulate_scenario(
                    base_data, scenario_name, params
                )
        else:
            results = self.scenario_simulator.run_what_if_scenarios(base_data)
        
        return results
    
    def analyze_policy_impact(self, baseline_data, policy_params=None):
        """Analyze impact of environmental policies"""
        return self.policy_modeler.simulate_policy_impact(baseline_data, policy_params or {})
    
    def validate_crowdsourced_data(self, user_readings, reference_readings=None):
        """Validate and fuse crowdsourced sensor data"""
        if len(user_readings) == 1 and reference_readings:
            # Single reading validation
            validation = self.data_validator.validate_sensor_reading(
                user_readings[0], reference_readings
            )
            return [validation]
        else:
            # Batch validation
            return self.data_validator.batch_validate_readings(user_readings)
    
    def get_spatial_predictions(self, sensor_data, target_locations):
        """Get AQI predictions for locations without sensors"""
        return self.spatial_interpolator.interpolate_aqi(sensor_data, target_locations)
    
    def chat_response(self, question, user_profile, current_aqi):
        """Get chatbot response for health questions"""
        return self.health_chatbot.get_response(question, user_profile, current_aqi)
    
    def generate_daily_summary(self, location_data, user_profile=None):
        """Generate daily air quality summary"""
        current_aqi = location_data.get('aqi', 50)
        
        summary = {
            'date': datetime.now().date(),
            'location': location_data.get('location', 'Unknown'),
            'current_aqi': current_aqi,
            'category': self.health_recommender.get_aqi_category(current_aqi),
            'color': self.health_recommender.get_severity_color(
                self.health_recommender.get_aqi_category(current_aqi)
            )
        }
        
        # Add forecast if available
        if self.models_trained['forecaster']:
            forecast = self.forecaster.forecast_hourly(location_data, hours=24)
            if forecast:
                max_aqi = max(f['predicted_aqi'] for f in forecast)
                min_aqi = min(f['predicted_aqi'] for f in forecast)
                summary['forecast'] = {
                    'max_aqi': max_aqi,
                    'min_aqi': min_aqi,
                    'trend': 'improving' if max_aqi < current_aqi else 'worsening' if min_aqi > current_aqi else 'stable'
                }
        
        # Add personalized recommendations
        if user_profile:
            recommendations = self.health_recommender.get_recommendations(
                current_aqi, user_profile, location_data
            )
            summary['recommendations'] = recommendations['recommendations'][:3]
        
        return summary
    
    def get_model_status(self):
        """Get status of all ML models"""
        return {
            'models_trained': self.models_trained,
            'last_updated': datetime.now(),
            'available_features': {
                'real_time_forecasting': self.models_trained['forecaster'],
                'anomaly_detection': self.models_trained['anomaly_detector'],
                'scenario_simulation': self.models_trained['scenario_simulator'],
                'health_recommendations': True,
                'data_validation': True,
                'spatial_interpolation': True
            }
        }