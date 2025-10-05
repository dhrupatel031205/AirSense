import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AQIAnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.threshold_multiplier = 2.0
        self.is_trained = False
    
    def prepare_features(self, data):
        """Prepare features for anomaly detection"""
        features = []
        for _, row in data.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            feature_row = [
                row['aqi'],
                row.get('pm25', 0),
                row.get('pm10', 0),
                row.get('no2', 0),
                row.get('o3', 0),
                timestamp.hour,
                timestamp.dayofweek
            ]
            features.append(feature_row)
        return np.array(features)
    
    def train(self, historical_data):
        """Train anomaly detection model"""
        X = self.prepare_features(historical_data)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
    
    def detect_anomalies(self, data):
        """Detect anomalies in AQI data"""
        if not self.is_trained:
            return [False] * len(data)
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        anomaly_scores = self.model.decision_function(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        results = []
        for i, (score, pred) in enumerate(zip(anomaly_scores, predictions)):
            is_anomaly = pred == -1
            severity = 'high' if score < -0.5 else 'medium' if score < -0.2 else 'low'
            
            results.append({
                'is_anomaly': is_anomaly,
                'severity': severity,
                'score': float(score),
                'aqi': data.iloc[i]['aqi']
            })
        
        return results
    
    def generate_alert(self, anomaly_result, location):
        """Generate alert message for anomaly"""
        if not anomaly_result['is_anomaly']:
            return None
        
        aqi = anomaly_result['aqi']
        severity = anomaly_result['severity']
        
        if aqi > 150:
            level = 'Critical'
            message = f"Critical AQI spike detected in {location}: {aqi}. Avoid outdoor activities."
        elif aqi > 100:
            level = 'High'
            message = f"High AQI anomaly in {location}: {aqi}. Limit outdoor exposure."
        else:
            level = 'Medium'
            message = f"Unusual AQI pattern in {location}: {aqi}. Monitor conditions."
        
        return {
            'level': level,
            'message': message,
            'aqi': aqi,
            'location': location,
            'severity': severity
        }

class PersonalizedAlerts:
    def __init__(self):
        self.health_thresholds = {
            'healthy': {'moderate': 50, 'unhealthy': 100},
            'sensitive': {'moderate': 35, 'unhealthy': 75},
            'respiratory': {'moderate': 25, 'unhealthy': 50},
            'heart_disease': {'moderate': 25, 'unhealthy': 50}
        }
    
    def get_personalized_threshold(self, user_profile):
        """Get personalized AQI threshold based on user health profile"""
        conditions = user_profile.get('conditions', [])
        age = user_profile.get('age', 30)
        
        if 'respiratory' in conditions or 'asthma' in conditions:
            profile_type = 'respiratory'
        elif 'heart_disease' in conditions:
            profile_type = 'heart_disease'
        elif age > 65 or age < 12:
            profile_type = 'sensitive'
        else:
            profile_type = 'healthy'
        
        return self.health_thresholds[profile_type]
    
    def should_alert(self, aqi, user_profile):
        """Determine if user should receive alert"""
        thresholds = self.get_personalized_threshold(user_profile)
        
        if aqi >= thresholds['unhealthy']:
            return {'alert': True, 'level': 'unhealthy', 'threshold': thresholds['unhealthy']}
        elif aqi >= thresholds['moderate']:
            return {'alert': True, 'level': 'moderate', 'threshold': thresholds['moderate']}
        
        return {'alert': False, 'level': 'good', 'threshold': 0}