import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta

class AQIForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, data):
        """Extract temporal and weather features"""
        features = []
        for _, row in data.iterrows():
            timestamp = pd.to_datetime(row['timestamp'])
            feature_row = [
                timestamp.hour,
                timestamp.dayofweek,
                timestamp.month,
                row.get('temperature', 20),
                row.get('humidity', 50),
                row.get('wind_speed', 5),
                row.get('no2', 0),
                row.get('o3', 0),
                row.get('pm25', 0),
                row.get('pm10', 0)
            ]
            features.append(feature_row)
        return np.array(features)
    
    def train(self, data):
        """Train the forecasting model"""
        X = self.prepare_features(data)
        y = data['aqi'].values
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict(self, data):
        """Predict AQI values"""
        if not self.is_trained:
            return np.zeros(len(data))
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def forecast_hourly(self, location_data, hours=24):
        """Generate hourly forecasts"""
        forecasts = []
        base_time = datetime.now()
        
        for h in range(hours):
            forecast_time = base_time + timedelta(hours=h)
            forecast_data = pd.DataFrame([{
                'timestamp': forecast_time,
                'temperature': location_data.get('temperature', 20),
                'humidity': location_data.get('humidity', 50),
                'wind_speed': location_data.get('wind_speed', 5),
                'no2': location_data.get('no2', 0),
                'o3': location_data.get('o3', 0),
                'pm25': location_data.get('pm25', 0),
                'pm10': location_data.get('pm10', 0)
            }])
            
            aqi_pred = self.predict(forecast_data)[0]
            forecasts.append({
                'timestamp': forecast_time,
                'predicted_aqi': max(0, int(aqi_pred))
            })
        
        return forecasts

class SpatialInterpolator:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
    
    def interpolate_aqi(self, sensor_data, target_locations):
        """Interpolate AQI for locations without sensors"""
        if len(sensor_data) < 3:
            return [50] * len(target_locations)  # Default moderate AQI
        
        # Prepare training data
        X_train = [[row['lat'], row['lon']] for _, row in sensor_data.iterrows()]
        y_train = sensor_data['aqi'].values
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        
        # Predict for target locations
        X_target = [[loc['lat'], loc['lon']] for loc in target_locations]
        X_target_scaled = self.scaler.transform(X_target)
        predictions = self.model.predict(X_target_scaled)
        
        return [max(0, int(pred)) for pred in predictions]