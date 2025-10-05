"""
Regression Model for Air Quality Prediction

This module contains various regression models for predicting air quality
based on meteorological data, historical trends, and other features.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from django.conf import settings
from datetime import datetime, timedelta


class AirQualityRegressor:
    """
    Ensemble regression model for air quality prediction
    """
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = self._initialize_model()
        self.scaler = StandardScaler()
        self.feature_names = None
        self.is_trained = False
        
    def _initialize_model(self):
        """Initialize the regression model based on type"""
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ),
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=1.0)
        }
        
        return models.get(self.model_type, models['random_forest'])
    
    def prepare_features(self, data):
        """
        Prepare features from raw data
        
        Args:
            data: Dictionary with meteorological and other data
            
        Returns:
            Feature array ready for model input
        """
        features = []
        
        # Meteorological features
        features.extend([
            data.get('temperature', 0),
            data.get('humidity', 0),
            data.get('pressure', 0),
            data.get('wind_speed', 0),
            data.get('wind_direction', 0),
            data.get('precipitation', 0),
        ])
        
        # Temporal features
        timestamp = data.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        features.extend([
            timestamp.hour,
            timestamp.weekday(),
            timestamp.month,
            timestamp.day,
        ])
        
        # Location features (if available)
        features.extend([
            data.get('latitude', 0),
            data.get('longitude', 0),
            data.get('elevation', 0),
        ])
        
        # Historical features (moving averages)
        features.extend([
            data.get('pm25_1h_avg', 0),
            data.get('pm25_24h_avg', 0),
            data.get('pm10_1h_avg', 0),
            data.get('no2_1h_avg', 0),
        ])
        
        self.feature_names = [
            'temperature', 'humidity', 'pressure', 'wind_speed', 'wind_direction', 'precipitation',
            'hour', 'weekday', 'month', 'day',
            'latitude', 'longitude', 'elevation',
            'pm25_1h_avg', 'pm25_24h_avg', 'pm10_1h_avg', 'no2_1h_avg'
        ]
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X, y, test_size=0.2):
        """
        Train the regression model
        
        Args:
            X: Feature matrix
            y: Target values
            test_size: Proportion of data for testing
            
        Returns:
            Dictionary with training metrics
        """
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'train_mse': mean_squared_error(y_train, y_train_pred),
            'test_mse': mean_squared_error(y_test, y_test_pred),
            'train_mae': mean_absolute_error(y_train, y_train_pred),
            'test_mae': mean_absolute_error(y_test, y_test_pred),
            'train_r2': r2_score(y_train, y_train_pred),
            'test_r2': r2_score(y_test, y_test_pred),
        }
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='r2')
        metrics['cv_r2_mean'] = cv_scores.mean()
        metrics['cv_r2_std'] = cv_scores.std()
        
        self.is_trained = True
        return metrics
    
    def predict(self, X):
        """Make predictions using the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        return predictions
    
    def get_feature_importance(self):
        """Get feature importance (if supported by model)"""
        if not self.is_trained:
            return None
            
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            if self.feature_names:
                return dict(zip(self.feature_names, importance))
            return importance
        return None
    
    def save_model(self, filepath):
        """Save the trained model and scaler"""
        if self.model is not None:
            model_dir = os.path.dirname(filepath)
            os.makedirs(model_dir, exist_ok=True)
            
            # Save model, scaler, and metadata
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'model_type': self.model_type,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained
            }, filepath + '_regression.pkl')
            
            print(f"Regression model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a pre-trained model"""
        try:
            data = joblib.load(filepath + '_regression.pkl')
            self.model = data['model']
            self.scaler = data['scaler']
            self.model_type = data['model_type']
            self.feature_names = data['feature_names']
            self.is_trained = data['is_trained']
            
            print(f"Regression model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


def get_regression_prediction(location, weather_data, historical_data=None):
    """
    Get air quality prediction using regression model
    
    Args:
        location: Location identifier
        weather_data: Current meteorological data
        historical_data: Historical air quality data
        
    Returns:
        Dictionary with prediction results
    """
    try:
        # Initialize and load model
        regressor = AirQualityRegressor('random_forest')
        model_path = os.path.join(settings.BASE_DIR, 'models', 'regression_air_quality')
        
        if not regressor.load_model(model_path):
            return {
                'error': 'Regression model not available',
                'prediction': None,
                'confidence': 0.0
            }
        
        # Combine weather and historical data
        combined_data = {**weather_data}
        if historical_data:
            combined_data.update(historical_data)
        
        # Prepare features
        features = regressor.prepare_features(combined_data)
        
        # Make prediction
        prediction = regressor.predict(features)[0]
        
        # Convert to AQI (assuming prediction is in concentration units)
        aqi_value = max(0, min(500, int(prediction)))
        
        # Calculate confidence based on model type and historical performance
        confidence = 0.75  # This should be calculated based on model validation metrics
        
        return {
            'prediction': aqi_value,
            'confidence': confidence,
            'model_type': f'Regression ({regressor.model_type})',
            'location': location,
            'features_used': regressor.feature_names
        }
        
    except Exception as e:
        return {
            'error': f'Regression prediction failed: {str(e)}',
            'prediction': None,
            'confidence': 0.0
        }


def create_training_dataset(location, start_date, end_date):
    """
    Create a training dataset for the regression model
    
    Args:
        location: Location to collect data for
        start_date: Start date for data collection
        end_date: End date for data collection
        
    Returns:
        Tuple of (features, targets) for model training
    """
    # This is a placeholder implementation
    # In a real scenario, this would:
    # 1. Query historical air quality data
    # 2. Query meteorological data for the same period
    # 3. Combine and align the datasets
    # 4. Create feature matrix and target vector
    
    print(f"Creating training dataset for {location} from {start_date} to {end_date}")
    
    # Return dummy data for now
    np.random.seed(42)
    n_samples = 1000
    n_features = 17  # Number of features from prepare_features
    
    X = np.random.randn(n_samples, n_features)
    y = np.random.randint(0, 200, n_samples)  # Random AQI values
    
    return X, y