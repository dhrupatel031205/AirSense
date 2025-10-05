import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

class ScenarioSimulator:
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_scenario_features(self, base_data, scenario_params):
        """Prepare features with scenario modifications"""
        features = []
        for _, row in base_data.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            
            # Apply scenario modifications
            temperature = row.get('temperature', 20) + scenario_params.get('temp_change', 0)
            wind_speed = max(0.1, row.get('wind_speed', 5) * scenario_params.get('wind_multiplier', 1.0))
            emissions = row.get('emissions', 1.0) * scenario_params.get('emission_multiplier', 1.0)
            
            feature_row = [
                timestamp.hour,
                timestamp.dayofweek,
                timestamp.month,
                temperature,
                row.get('humidity', 50),
                wind_speed,
                emissions,
                scenario_params.get('wildfire_intensity', 0),
                scenario_params.get('traffic_multiplier', 1.0)
            ]
            features.append(feature_row)
        
        return np.array(features)
    
    def train(self, historical_data):
        """Train scenario simulation model"""
        X = self.prepare_scenario_features(historical_data, {})
        y = historical_data['aqi'].values
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def simulate_scenario(self, base_data, scenario_name, scenario_params):
        """Simulate AQI under different scenarios"""
        if not self.is_trained:
            return base_data['aqi'].values
        
        X = self.prepare_scenario_features(base_data, scenario_params)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return {
            'scenario': scenario_name,
            'predictions': [max(0, int(pred)) for pred in predictions],
            'avg_change': np.mean(predictions) - np.mean(base_data['aqi']),
            'max_aqi': int(np.max(predictions))
        }
    
    def run_what_if_scenarios(self, base_data):
        """Run predefined what-if scenarios"""
        scenarios = {
            'wildfire_nearby': {
                'emission_multiplier': 2.5,
                'wildfire_intensity': 0.8,
                'temp_change': 5
            },
            'heavy_traffic': {
                'traffic_multiplier': 2.0,
                'emission_multiplier': 1.5
            },
            'strong_winds': {
                'wind_multiplier': 3.0,
                'emission_multiplier': 0.7
            },
            'temperature_spike': {
                'temp_change': 10,
                'emission_multiplier': 1.3
            },
            'industrial_shutdown': {
                'emission_multiplier': 0.3
            }
        }
        
        results = {}
        for scenario_name, params in scenarios.items():
            results[scenario_name] = self.simulate_scenario(base_data, scenario_name, params)
        
        return results

class PolicyImpactModeler:
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
    
    def simulate_policy_impact(self, baseline_data, policy_params):
        """Simulate impact of environmental policies"""
        policy_scenarios = {
            'emission_reduction_20': {'emission_multiplier': 0.8},
            'emission_reduction_50': {'emission_multiplier': 0.5},
            'traffic_restriction': {'traffic_multiplier': 0.6, 'emission_multiplier': 0.85},
            'industrial_regulation': {'emission_multiplier': 0.7},
            'green_transport': {'traffic_multiplier': 0.4, 'emission_multiplier': 0.6}
        }
        
        simulator = ScenarioSimulator()
        simulator.model = self.model
        simulator.scaler = self.scaler
        simulator.is_trained = True
        
        results = {}
        for policy_name, params in policy_scenarios.items():
            if policy_name in policy_params or not policy_params:
                results[policy_name] = simulator.simulate_scenario(
                    baseline_data, policy_name, params
                )
        
        return results
    
    def calculate_health_benefits(self, baseline_aqi, improved_aqi):
        """Calculate estimated health benefits from AQI improvement"""
        aqi_reduction = baseline_aqi - improved_aqi
        
        if aqi_reduction <= 0:
            return {'benefit': 'none', 'description': 'No improvement in air quality'}
        
        if aqi_reduction >= 50:
            return {
                'benefit': 'high',
                'description': f'Significant health improvement: {aqi_reduction:.1f} AQI reduction',
                'estimated_impact': 'Reduced respiratory issues, improved cardiovascular health'
            }
        elif aqi_reduction >= 20:
            return {
                'benefit': 'medium',
                'description': f'Moderate health improvement: {aqi_reduction:.1f} AQI reduction',
                'estimated_impact': 'Reduced symptoms for sensitive groups'
            }
        else:
            return {
                'benefit': 'low',
                'description': f'Minor health improvement: {aqi_reduction:.1f} AQI reduction',
                'estimated_impact': 'Slight improvement in air quality'
            }