import numpy as np
from datetime import datetime

class HealthRecommender:
    def __init__(self):
        self.recommendations = {
            'good': {
                'general': ['Enjoy outdoor activities', 'Perfect time for exercise'],
                'sensitive': ['Great day for outdoor activities', 'No special precautions needed']
            },
            'moderate': {
                'general': ['Outdoor activities are acceptable', 'Consider reducing prolonged outdoor exertion'],
                'sensitive': ['Limit prolonged outdoor activities', 'Watch for symptoms']
            },
            'unhealthy_sensitive': {
                'general': ['Reduce outdoor activities', 'Limit time outside'],
                'sensitive': ['Avoid outdoor activities', 'Stay indoors when possible']
            },
            'unhealthy': {
                'general': ['Avoid outdoor activities', 'Use air purifiers indoors'],
                'sensitive': ['Stay indoors', 'Use masks if going outside', 'Run air purifiers']
            },
            'very_unhealthy': {
                'general': ['Stay indoors', 'Avoid all outdoor activities', 'Use air purifiers'],
                'sensitive': ['Emergency precautions', 'Stay indoors with air purification', 'Seek medical advice if symptoms occur']
            },
            'hazardous': {
                'general': ['Emergency conditions', 'Stay indoors', 'Seal windows and doors'],
                'sensitive': ['Emergency conditions', 'Stay indoors with air purification', 'Contact healthcare provider']
            }
        }
    
    def get_aqi_category(self, aqi):
        """Categorize AQI value"""
        if aqi <= 50:
            return 'good'
        elif aqi <= 100:
            return 'moderate'
        elif aqi <= 150:
            return 'unhealthy_sensitive'
        elif aqi <= 200:
            return 'unhealthy'
        elif aqi <= 300:
            return 'very_unhealthy'
        else:
            return 'hazardous'
    
    def get_user_risk_level(self, user_profile):
        """Determine user risk level based on profile"""
        age = user_profile.get('age', 30)
        conditions = user_profile.get('conditions', [])
        
        high_risk_conditions = ['asthma', 'copd', 'heart_disease', 'respiratory']
        
        if any(condition in high_risk_conditions for condition in conditions):
            return 'sensitive'
        elif age < 12 or age > 65:
            return 'sensitive'
        else:
            return 'general'
    
    def get_recommendations(self, aqi, user_profile, pollutant_data=None):
        """Get personalized health recommendations"""
        category = self.get_aqi_category(aqi)
        risk_level = self.get_user_risk_level(user_profile)
        
        base_recommendations = self.recommendations[category][risk_level].copy()
        
        # Add pollutant-specific recommendations
        if pollutant_data:
            if pollutant_data.get('pm25', 0) > 35:
                base_recommendations.append('High PM2.5 levels - use N95 masks outdoors')
            if pollutant_data.get('o3', 0) > 70:
                base_recommendations.append('High ozone - avoid outdoor exercise during peak hours')
            if pollutant_data.get('no2', 0) > 100:
                base_recommendations.append('High NO2 levels - avoid busy roads')
        
        # Add time-specific recommendations
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 10 or 16 <= current_hour <= 19:
            if category in ['unhealthy_sensitive', 'unhealthy']:
                base_recommendations.append('Rush hour - pollution levels may be higher near roads')
        
        return {
            'aqi': aqi,
            'category': category,
            'risk_level': risk_level,
            'recommendations': base_recommendations,
            'severity_color': self.get_severity_color(category)
        }
    
    def get_severity_color(self, category):
        """Get color code for AQI category"""
        colors = {
            'good': '#10b981',
            'moderate': '#f59e0b',
            'unhealthy_sensitive': '#f97316',
            'unhealthy': '#ef4444',
            'very_unhealthy': '#8b5cf6',
            'hazardous': '#7c2d12'
        }
        return colors.get(category, '#6b7280')
    
    def get_activity_recommendations(self, aqi, activity_type):
        """Get activity-specific recommendations"""
        category = self.get_aqi_category(aqi)
        
        activity_guidance = {
            'exercise': {
                'good': 'Excellent conditions for all exercise',
                'moderate': 'Good for most exercise, sensitive people should watch for symptoms',
                'unhealthy_sensitive': 'Reduce intensity and duration of outdoor exercise',
                'unhealthy': 'Avoid outdoor exercise, exercise indoors instead',
                'very_unhealthy': 'Avoid all outdoor exercise',
                'hazardous': 'Avoid all outdoor exercise'
            },
            'commuting': {
                'good': 'Normal commuting conditions',
                'moderate': 'Consider alternative routes away from heavy traffic',
                'unhealthy_sensitive': 'Use public transport or carpool to reduce exposure time',
                'unhealthy': 'Work from home if possible, use masks during commute',
                'very_unhealthy': 'Avoid unnecessary travel, work from home',
                'hazardous': 'Avoid all unnecessary travel'
            },
            'outdoor_work': {
                'good': 'Normal outdoor work conditions',
                'moderate': 'Take regular breaks, stay hydrated',
                'unhealthy_sensitive': 'Limit outdoor work hours, use protective equipment',
                'unhealthy': 'Minimize outdoor work, use N95 masks',
                'very_unhealthy': 'Postpone non-essential outdoor work',
                'hazardous': 'Suspend all outdoor work activities'
            }
        }
        
        return activity_guidance.get(activity_type, {}).get(category, 'Monitor air quality conditions')

class HealthChatbot:
    def __init__(self):
        self.recommender = HealthRecommender()
        self.faq_responses = {
            'what is aqi': 'AQI (Air Quality Index) is a measure of how polluted the air is. It ranges from 0-500, with higher numbers indicating worse air quality.',
            'is it safe to exercise': 'Exercise safety depends on current AQI levels and your health profile. Check your personalized recommendations.',
            'should i wear a mask': 'Masks are recommended when AQI is above 100, especially N95 masks for PM2.5 protection.',
            'air purifier help': 'Air purifiers with HEPA filters can reduce indoor PM2.5 levels by 50-80% when used properly.',
            'symptoms': 'Common symptoms of air pollution exposure include coughing, throat irritation, chest tightness, and eye irritation.'
        }
    
    def get_response(self, question, user_profile, current_aqi):
        """Generate chatbot response based on question and context"""
        question_lower = question.lower()
        
        # Check for FAQ matches
        for key, response in self.faq_responses.items():
            if key in question_lower:
                return response
        
        # Activity-specific questions
        if 'exercise' in question_lower or 'workout' in question_lower:
            return self.recommender.get_activity_recommendations(current_aqi, 'exercise')
        elif 'commute' in question_lower or 'travel' in question_lower:
            return self.recommender.get_activity_recommendations(current_aqi, 'commuting')
        elif 'work outside' in question_lower:
            return self.recommender.get_activity_recommendations(current_aqi, 'outdoor_work')
        
        # General health question
        recommendations = self.recommender.get_recommendations(current_aqi, user_profile)
        return f"Based on current AQI of {current_aqi}, here are your recommendations: {', '.join(recommendations['recommendations'][:2])}"