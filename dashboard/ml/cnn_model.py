"""
CNN Model for Air Quality Prediction

This module contains the Convolutional Neural Network model for predicting
air quality based on satellite imagery and meteorological data.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings


class AirQualityCNN:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def build_model(self, input_shape=(64, 64, 3)):
        """Build the CNN architecture"""
        model = keras.Sequential([
            # First Conv Block
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Second Conv Block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Third Conv Block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Flatten and Dense layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='linear')  # Regression output
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        self.model = model
        return model
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=100):
        """Train the CNN model"""
        if self.model is None:
            self.build_model(input_shape=X_train.shape[1:])
        
        # Scale the target values
        y_train_scaled = self.scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
        
        validation_data = None
        if X_val is not None and y_val is not None:
            y_val_scaled = self.scaler.transform(y_val.reshape(-1, 1)).flatten()
            validation_data = (X_val, y_val_scaled)
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(patience=5, factor=0.5)
        ]
        
        history = self.model.fit(
            X_train, y_train_scaled,
            epochs=epochs,
            batch_size=32,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )
        
        self.is_trained = True
        return history
    
    def predict(self, X):
        """Make predictions using the trained model"""
        if not self.is_trained or self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        predictions_scaled = self.model.predict(X)
        predictions = self.scaler.inverse_transform(predictions_scaled.reshape(-1, 1)).flatten()
        return predictions
    
    def save_model(self, filepath):
        """Save the trained model and scaler"""
        if self.model is not None:
            model_dir = os.path.dirname(filepath)
            os.makedirs(model_dir, exist_ok=True)
            
            # Save the model
            self.model.save(filepath + '_model.h5')
            
            # Save the scaler
            joblib.dump(self.scaler, filepath + '_scaler.pkl')
            
            print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a pre-trained model and scaler"""
        try:
            # Load the model
            self.model = keras.models.load_model(filepath + '_model.h5')
            
            # Load the scaler
            self.scaler = joblib.load(filepath + '_scaler.pkl')
            
            self.is_trained = True
            print(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


def preprocess_satellite_image(image_data):
    """
    Preprocess satellite image data for CNN input
    
    Args:
        image_data: Raw satellite image data
        
    Returns:
        Preprocessed image array ready for model input
    """
    # Placeholder preprocessing logic
    # In a real implementation, this would handle:
    # - Image normalization
    # - Resizing to model input dimensions
    # - Channel arrangement
    # - Data augmentation if needed
    
    if isinstance(image_data, str):
        # Load image from file path
        import cv2
        image = cv2.imread(image_data)
        image = cv2.resize(image, (64, 64))
        image = image / 255.0  # Normalize to 0-1
    else:
        # Assume it's already a numpy array
        image = np.array(image_data)
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = image / 255.0 if image.max() > 1 else image
    
    return image


def get_cnn_prediction(location, satellite_data):
    """
    Get air quality prediction using CNN model
    
    Args:
        location: Location identifier
        satellite_data: Satellite image data or file path
        
    Returns:
        Dictionary with prediction results
    """
    try:
        # Initialize and load model
        cnn_model = AirQualityCNN()
        model_path = os.path.join(settings.BASE_DIR, 'models', 'cnn_air_quality')
        
        if not cnn_model.load_model(model_path):
            return {
                'error': 'CNN model not available',
                'prediction': None,
                'confidence': 0.0
            }
        
        # Preprocess input data
        processed_image = preprocess_satellite_image(satellite_data)
        
        # Make prediction
        prediction = cnn_model.predict(np.expand_dims(processed_image, axis=0))[0]
        
        # Convert to AQI (placeholder logic)
        aqi_value = max(0, min(500, int(prediction * 100)))
        
        # Calculate confidence (placeholder)
        confidence = 0.85  # This should be calculated based on model uncertainty
        
        return {
            'prediction': aqi_value,
            'confidence': confidence,
            'model_type': 'CNN',
            'location': location
        }
        
    except Exception as e:
        return {
            'error': f'CNN prediction failed: {str(e)}',
            'prediction': None,
            'confidence': 0.0
        }