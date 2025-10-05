import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class CrowdsourcedDataValidator:
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.15, random_state=42)
        self.scaler = StandardScaler()
        self.reference_data = None
    
    def set_reference_data(self, nasa_data, openaq_data):
        """Set reference data from trusted sources"""
        self.reference_data = {
            'nasa': nasa_data,
            'openaq': openaq_data
        }
    
    def validate_sensor_reading(self, user_reading, nearby_reference_readings):
        """Validate a single sensor reading against reference data"""
        if not nearby_reference_readings:
            return {'valid': True, 'confidence': 0.5, 'reason': 'No reference data available'}
        
        user_aqi = user_reading.get('aqi', 0)
        reference_aqis = [r.get('aqi', 0) for r in nearby_reference_readings]
        
        if not reference_aqis:
            return {'valid': True, 'confidence': 0.5, 'reason': 'No reference AQI data'}
        
        avg_reference = np.mean(reference_aqis)
        std_reference = np.std(reference_aqis) if len(reference_aqis) > 1 else 20
        
        # Calculate deviation from reference
        deviation = abs(user_aqi - avg_reference)
        threshold = max(30, 2 * std_reference)
        
        if deviation <= threshold:
            confidence = max(0.7, 1 - (deviation / threshold) * 0.3)
            return {'valid': True, 'confidence': confidence, 'reason': 'Within expected range'}
        else:
            confidence = max(0.1, 1 - (deviation / (threshold * 2)))
            return {'valid': False, 'confidence': confidence, 'reason': f'Deviation too high: {deviation:.1f} from reference {avg_reference:.1f}'}
    
    def batch_validate_readings(self, user_readings):
        """Validate multiple sensor readings"""
        if len(user_readings) < 5:
            return [{'valid': True, 'confidence': 0.6, 'reason': 'Insufficient data for batch validation'}] * len(user_readings)
        
        # Prepare features for anomaly detection
        features = []
        for reading in user_readings:
            feature_row = [
                reading.get('aqi', 0),
                reading.get('pm25', 0),
                reading.get('pm10', 0),
                reading.get('temperature', 20),
                reading.get('humidity', 50)
            ]
            features.append(feature_row)
        
        X = np.array(features)
        X_scaled = self.scaler.fit_transform(X)
        
        # Detect anomalies
        anomaly_scores = self.anomaly_detector.fit_predict(X_scaled)
        decision_scores = self.anomaly_detector.decision_function(X_scaled)
        
        results = []
        for i, (anomaly, score) in enumerate(zip(anomaly_scores, decision_scores)):
            if anomaly == -1:  # Anomaly detected
                confidence = max(0.1, 0.5 + score * 0.5)
                results.append({
                    'valid': False,
                    'confidence': confidence,
                    'reason': f'Statistical anomaly detected (score: {score:.2f})'
                })
            else:
                confidence = min(0.9, 0.7 + abs(score) * 0.2)
                results.append({
                    'valid': True,
                    'confidence': confidence,
                    'reason': 'Passes statistical validation'
                })
        
        return results
    
    def fuse_data_sources(self, user_data, reference_data, validation_results):
        """Fuse user data with reference data based on validation confidence"""
        fused_readings = []
        
        for i, (user_reading, ref_reading, validation) in enumerate(zip(user_data, reference_data, validation_results)):
            confidence = validation['confidence']
            
            if confidence >= 0.7:
                # High confidence - use user data with slight reference adjustment
                weight_user = 0.8
                weight_ref = 0.2
            elif confidence >= 0.4:
                # Medium confidence - balanced fusion
                weight_user = 0.5
                weight_ref = 0.5
            else:
                # Low confidence - prefer reference data
                weight_user = 0.2
                weight_ref = 0.8
            
            fused_aqi = (user_reading.get('aqi', 0) * weight_user + 
                        ref_reading.get('aqi', 0) * weight_ref)
            
            fused_reading = {
                'aqi': int(fused_aqi),
                'pm25': user_reading.get('pm25', ref_reading.get('pm25', 0)),
                'pm10': user_reading.get('pm10', ref_reading.get('pm10', 0)),
                'confidence': confidence,
                'source': 'fused',
                'user_weight': weight_user,
                'reference_weight': weight_ref
            }
            
            fused_readings.append(fused_reading)
        
        return fused_readings

class DataQualityMetrics:
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
    
    def calculate_sensor_reliability(self, sensor_history):
        """Calculate reliability score for a sensor based on historical validation"""
        if not sensor_history:
            return 0.5  # Neutral score for new sensors
        
        valid_readings = sum(1 for reading in sensor_history if reading.get('valid', True))
        total_readings = len(sensor_history)
        
        reliability = valid_readings / total_readings if total_readings > 0 else 0.5
        
        # Adjust based on consistency
        if total_readings >= 10:
            recent_readings = sensor_history[-10:]
            recent_reliability = sum(1 for r in recent_readings if r.get('valid', True)) / len(recent_readings)
            reliability = (reliability * 0.7) + (recent_reliability * 0.3)
        
        return reliability
    
    def get_data_quality_label(self, confidence_score):
        """Get quality label based on confidence score"""
        for label, threshold in self.quality_thresholds.items():
            if confidence_score >= threshold:
                return label
        return 'poor'
    
    def generate_quality_report(self, validation_results):
        """Generate data quality report"""
        total_readings = len(validation_results)
        valid_readings = sum(1 for r in validation_results if r['valid'])
        avg_confidence = np.mean([r['confidence'] for r in validation_results])
        
        quality_distribution = {}
        for result in validation_results:
            quality = self.get_data_quality_label(result['confidence'])
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        return {
            'total_readings': total_readings,
            'valid_readings': valid_readings,
            'validation_rate': valid_readings / total_readings if total_readings > 0 else 0,
            'average_confidence': avg_confidence,
            'quality_distribution': quality_distribution,
            'overall_quality': self.get_data_quality_label(avg_confidence)
        }