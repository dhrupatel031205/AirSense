"""
Policy recommendation engine

This module contains logic for analyzing air quality data and providing
personalized policy recommendations based on user location, health profile,
and current environmental conditions.
"""

from django.db.models import Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import EnvironmentalPolicy, PolicyCategory, UserEcoProfile
from dashboard.models import AirQualityReading, UserLocationPreference
from health_alerts.models import UserHealthProfile
import logging

logger = logging.getLogger(__name__)


def get_personalized_recommendations(user, location=None):
    """
    Get personalized policy recommendations for a user
    
    Args:
        user: User object
        location: Specific location to get recommendations for
        
    Returns:
        Dictionary with categorized recommendations
    """
    try:
        # Get user's locations if not specified
        if not location:
            user_locations = UserLocationPreference.objects.filter(
                user=user,
                is_primary=True
            ).first()
            location = user_locations.location_name if user_locations else None
        
        if not location:
            return get_general_recommendations()
        
        # Get current air quality conditions
        current_aqi = get_current_air_quality(location)
        
        # Get user profiles
        try:
            health_profile = UserHealthProfile.objects.get(user=user)
        except UserHealthProfile.DoesNotExist:
            health_profile = None
        
        try:
            eco_profile = UserEcoProfile.objects.get(user=user)
        except UserEcoProfile.DoesNotExist:
            eco_profile = None
        
        # Generate recommendations based on conditions
        recommendations = {
            'immediate': [],
            'short_term': [],
            'long_term': [],
            'community': [],
            'policy_support': []
        }
        
        # Immediate recommendations based on current AQI
        if current_aqi and current_aqi['aqi'] > 100:
            recommendations['immediate'].extend(
                get_immediate_action_recommendations(current_aqi, health_profile)
            )
        
        # Short-term recommendations
        recommendations['short_term'].extend(
            get_short_term_recommendations(location, current_aqi, health_profile)
        )
        
        # Long-term policy recommendations
        recommendations['long_term'].extend(
            get_long_term_policy_recommendations(location, eco_profile)
        )
        
        # Community action recommendations
        recommendations['community'].extend(
            get_community_recommendations(location, eco_profile)
        )
        
        # Policy support recommendations
        recommendations['policy_support'].extend(
            get_policy_support_recommendations(location, eco_profile)
        )
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating personalized recommendations: {e}")
        return get_general_recommendations()


def get_current_air_quality(location):
    """Get current air quality data for location"""
    try:
        latest_reading = AirQualityReading.objects.filter(
            location=location
        ).first()
        
        if latest_reading:
            return {
                'aqi': latest_reading.aqi_value,
                'pollutant': latest_reading.pollutant_type,
                'concentration': latest_reading.concentration,
                'timestamp': latest_reading.timestamp
            }
    except Exception as e:
        logger.error(f"Error getting air quality for {location}: {e}")
    
    return None


def get_immediate_action_recommendations(current_aqi, health_profile):
    """Get immediate action recommendations based on current AQI"""
    recommendations = []
    aqi_value = current_aqi['aqi']
    
    if aqi_value > 200:
        recommendations.extend([
            {
                'title': 'Stay Indoors',
                'description': 'Avoid all outdoor activities. Keep windows and doors closed.',
                'priority': 'critical',
                'type': 'immediate'
            },
            {
                'title': 'Use Air Purifiers',
                'description': 'Run air purifiers on high settings if available.',
                'priority': 'high',
                'type': 'immediate'
            }
        ])
    elif aqi_value > 150:
        recommendations.extend([
            {
                'title': 'Limit Outdoor Activities',
                'description': 'Reduce time spent outdoors, especially strenuous activities.',
                'priority': 'high',
                'type': 'immediate'
            },
            {
                'title': 'Wear N95 Masks',
                'description': 'Consider wearing N95 masks when going outside.',
                'priority': 'medium',
                'type': 'immediate'
            }
        ])
    elif aqi_value > 100:
        recommendations.append({
            'title': 'Monitor Symptoms',
            'description': 'Be aware of any respiratory symptoms and limit prolonged outdoor exposure.',
            'priority': 'medium',
            'type': 'immediate'
        })
    
    # Add health-specific recommendations
    if health_profile and health_profile.conditions.exists():
        if aqi_value > 100:
            recommendations.append({
                'title': 'Health Condition Alert',
                'description': 'Given your health conditions, take extra precautions and consider consulting your healthcare provider.',
                'priority': 'high',
                'type': 'immediate'
            })
    
    return recommendations


def get_short_term_recommendations(location, current_aqi, health_profile):
    """Get short-term recommendations for the next few days"""
    recommendations = []
    
    # Check historical trends
    week_ago = timezone.now() - timedelta(days=7)
    recent_readings = AirQualityReading.objects.filter(
        location=location,
        timestamp__gte=week_ago
    )
    
    if recent_readings.exists():
        avg_aqi = recent_readings.aggregate(Avg('aqi_value'))['aqi_value__avg']
        
        if avg_aqi > 100:
            recommendations.extend([
                {
                    'title': 'Plan Indoor Activities',
                    'description': 'Air quality has been consistently poor. Plan more indoor activities for the week.',
                    'priority': 'medium',
                    'type': 'planning'
                },
                {
                    'title': 'Check Air Quality Apps',
                    'description': 'Monitor air quality forecasts daily to plan your activities.',
                    'priority': 'low',
                    'type': 'planning'
                }
            ])
    
    # Seasonal recommendations
    current_month = timezone.now().month
    if current_month in [6, 7, 8]:  # Summer months
        recommendations.append({
            'title': 'Wildfire Season Preparation',
            'description': 'Prepare for potential wildfire smoke. Stock up on N95 masks and air filters.',
            'priority': 'medium',
            'type': 'seasonal'
        })
    elif current_month in [11, 12, 1, 2]:  # Winter months
        recommendations.append({
            'title': 'Winter Air Quality',
            'description': 'Wood burning and heating can worsen air quality. Consider alternatives.',
            'priority': 'low',
            'type': 'seasonal'
        })
    
    return recommendations


def get_long_term_policy_recommendations(location, eco_profile):
    """Get long-term policy recommendations"""
    recommendations = []
    
    # Get relevant policies for location
    local_policies = EnvironmentalPolicy.objects.filter(
        Q(location__icontains=location) | Q(location=''),
        policy_type__in=['local', 'regional'],
        is_active=True
    )[:3]
    
    for policy in local_policies:
        recommendations.append({
            'title': f'Support: {policy.title}',
            'description': policy.description[:200] + '...' if len(policy.description) > 200 else policy.description,
            'priority': 'medium' if policy.impact_level == 'high' else 'low',
            'type': 'policy',
            'policy_id': policy.id,
            'url': f'/eco-action/policies/{policy.id}/'
        })
    
    # General long-term recommendations
    recommendations.extend([
        {
            'title': 'Advocate for Clean Transportation',
            'description': 'Support policies that promote electric vehicles and public transportation.',
            'priority': 'medium',
            'type': 'advocacy'
        },
        {
            'title': 'Promote Renewable Energy',
            'description': 'Advocate for renewable energy initiatives in your community.',
            'priority': 'medium',
            'type': 'advocacy'
        }
    ])
    
    return recommendations


def get_community_recommendations(location, eco_profile):
    """Get community action recommendations"""
    recommendations = []
    
    # Import here to avoid circular imports
    from .models import CommunityAction
    
    # Get local community actions
    local_actions = CommunityAction.objects.filter(
        location__icontains=location,
        status__in=['planning', 'active'],
        start_date__gte=timezone.now()
    )[:3]
    
    for action in local_actions:
        recommendations.append({
            'title': f'Join: {action.title}',
            'description': action.description[:200] + '...' if len(action.description) > 200 else action.description,
            'priority': 'medium',
            'type': 'community_action',
            'action_id': action.id,
            'url': f'/eco-action/community-actions/{action.id}/',
            'date': action.start_date
        })
    
    # General community recommendations
    if not local_actions:
        recommendations.extend([
            {
                'title': 'Start a Community Garden',
                'description': 'Organize a local community garden to improve air quality and community engagement.',
                'priority': 'low',
                'type': 'community_suggestion'
            },
            {
                'title': 'Organize Clean Air Advocacy',
                'description': 'Start a local group focused on air quality awareness and advocacy.',
                'priority': 'medium',
                'type': 'community_suggestion'
            }
        ])
    
    return recommendations


def get_policy_support_recommendations(location, eco_profile):
    """Get policy support recommendations"""
    recommendations = []
    
    # Get high-impact policies that need support
    high_impact_policies = EnvironmentalPolicy.objects.filter(
        impact_level='high',
        is_active=True
    ).exclude(
        Q(location__icontains=location) & ~Q(location='')
    )[:2]
    
    for policy in high_impact_policies:
        recommendations.append({
            'title': f'Support National Policy: {policy.title}',
            'description': f'This {policy.policy_type} policy could significantly impact air quality nationwide.',
            'priority': 'low',
            'type': 'national_policy',
            'policy_id': policy.id,
            'url': f'/eco-action/policies/{policy.id}/'
        })
    
    return recommendations


def get_general_recommendations():
    """Get general recommendations when user-specific data is not available"""
    return {
        'immediate': [
            {
                'title': 'Monitor Air Quality',
                'description': 'Check daily air quality reports before planning outdoor activities.',
                'priority': 'medium',
                'type': 'general'
            }
        ],
        'short_term': [
            {
                'title': 'Set Up Location Preferences',
                'description': 'Add your location to receive personalized air quality alerts.',
                'priority': 'high',
                'type': 'setup'
            }
        ],
        'long_term': [
            {
                'title': 'Learn About Air Quality',
                'description': 'Educate yourself about air quality sources and health impacts.',
                'priority': 'medium',
                'type': 'education'
            }
        ],
        'community': [
            {
                'title': 'Find Local Groups',
                'description': 'Connect with environmental groups in your area.',
                'priority': 'low',
                'type': 'networking'
            }
        ],
        'policy_support': [
            {
                'title': 'Stay Informed',
                'description': 'Follow environmental policy news and updates.',
                'priority': 'low',
                'type': 'awareness'
            }
        ]
    }


def analyze_policy_effectiveness(policy_id):
    """
    Analyze the effectiveness of a policy based on air quality trends
    
    Args:
        policy_id: ID of the policy to analyze
        
    Returns:
        Dictionary with effectiveness analysis
    """
    try:
        policy = EnvironmentalPolicy.objects.get(id=policy_id)
        
        if not policy.implementation_date:
            return {
                'status': 'not_implemented',
                'message': 'Policy has not been implemented yet'
            }
        
        # Get air quality data before and after implementation
        implementation_date = policy.implementation_date
        before_date = implementation_date - timedelta(days=365)  # 1 year before
        after_date = implementation_date + timedelta(days=365)   # 1 year after
        
        before_readings = AirQualityReading.objects.filter(
            location__icontains=policy.location if policy.location else '',
            timestamp__gte=before_date,
            timestamp__lt=implementation_date
        )
        
        after_readings = AirQualityReading.objects.filter(
            location__icontains=policy.location if policy.location else '',
            timestamp__gte=implementation_date,
            timestamp__lt=after_date
        )
        
        if not before_readings.exists() or not after_readings.exists():
            return {
                'status': 'insufficient_data',
                'message': 'Insufficient air quality data to analyze effectiveness'
            }
        
        before_avg = before_readings.aggregate(Avg('aqi_value'))['aqi_value__avg']
        after_avg = after_readings.aggregate(Avg('aqi_value'))['aqi_value__avg']
        
        improvement = before_avg - after_avg
        improvement_percent = (improvement / before_avg) * 100
        
        return {
            'status': 'analyzed',
            'before_avg_aqi': round(before_avg, 1),
            'after_avg_aqi': round(after_avg, 1),
            'improvement': round(improvement, 1),
            'improvement_percent': round(improvement_percent, 1),
            'effectiveness': 'positive' if improvement > 0 else 'negative' if improvement < -5 else 'neutral'
        }
        
    except EnvironmentalPolicy.DoesNotExist:
        return {
            'status': 'error',
            'message': 'Policy not found'
        }
    except Exception as e:
        logger.error(f"Error analyzing policy effectiveness: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


def get_trending_policies(days=30, limit=5):
    """
    Get trending policies based on recent feedback activity
    
    Args:
        days: Number of days to look back for trending analysis
        limit: Maximum number of policies to return
        
    Returns:
        List of trending policy objects
    """
    try:
        from .models import PolicyFeedback
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get policies with most recent feedback activity
        trending_policies = EnvironmentalPolicy.objects.filter(
            is_active=True,
            policyfeedback__created_at__gte=cutoff_date
        ).annotate(
            feedback_count=Count('policyfeedback')
        ).order_by('-feedback_count')[:limit]
        
        return trending_policies
        
    except Exception as e:
        logger.error(f"Error getting trending policies: {e}")
        return []