"""
Notification system for health alerts

This module handles sending notifications via email, SMS, and push notifications
when air quality conditions warrant health alerts.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Alert, UserHealthProfile, AlertTemplate
from dashboard.models import AirQualityReading, UserLocationPreference
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def create_health_alert(user, location, aqi_reading, alert_type='aqi_threshold'):
    """
    Create a health alert for a user based on air quality conditions
    
    Args:
        user: User object
        location: Location name
        aqi_reading: AirQualityReading object
        alert_type: Type of alert to create
        
    Returns:
        Alert object or None if alert not needed
    """
    try:
        # Get user's health profile
        try:
            health_profile = UserHealthProfile.objects.get(user=user)
        except UserHealthProfile.DoesNotExist:
            health_profile = UserHealthProfile.objects.create(user=user)
        
        # Check if alert is needed based on thresholds
        threshold = health_profile.custom_threshold
        
        # Adjust threshold based on health conditions
        if health_profile.conditions.exists():
            # Lower threshold for users with health conditions
            threshold = min(threshold, 75)
        
        if aqi_reading.aqi_value < threshold:
            return None  # No alert needed
        
        # Determine severity
        severity = determine_alert_severity(aqi_reading.aqi_value, health_profile)
        
        # Get or create alert template
        template = get_alert_template(alert_type)
        
        # Create alert message
        title = template.title_template.format(
            location=location,
            aqi=aqi_reading.aqi_value,
            pollutant=aqi_reading.pollutant_type
        )
        
        message = template.message_template.format(
            location=location,
            aqi=aqi_reading.aqi_value,
            pollutant=aqi_reading.pollutant_type,
            concentration=aqi_reading.concentration,
            timestamp=aqi_reading.timestamp.strftime('%Y-%m-%d %H:%M'),
            threshold=threshold
        )
        
        # Check for duplicate recent alerts
        recent_alert = Alert.objects.filter(
            user=user,
            location=location,
            alert_type=alert_type,
            created_at__gte=timezone.now() - timedelta(hours=1)
        ).first()
        
        if recent_alert and health_profile.alert_frequency != 'immediate':
            return recent_alert  # Don't create duplicate alert
        
        # Create the alert
        alert = Alert.objects.create(
            user=user,
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            location=location,
            aqi_value=aqi_reading.aqi_value,
            pollutant=aqi_reading.pollutant_type
        )
        
        # Send notifications
        send_alert_notifications(alert, health_profile)
        
        logger.info(f"Created health alert for user {user.username}: {title}")
        return alert
        
    except Exception as e:
        logger.error(f"Error creating health alert for user {user.username}: {e}")
        return None


def determine_alert_severity(aqi_value, health_profile):
    """Determine alert severity based on AQI and user profile"""
    if health_profile.conditions.exists() and aqi_value > 100:
        # More severe for users with health conditions
        if aqi_value > 200:
            return 'critical'
        elif aqi_value > 150:
            return 'high'
        else:
            return 'medium'
    else:
        # Standard severity levels
        if aqi_value > 300:
            return 'critical'
        elif aqi_value > 200:
            return 'high'
        elif aqi_value > 150:
            return 'medium'
        else:
            return 'low'


def get_alert_template(alert_type):
    """Get or create alert template for given type"""
    try:
        return AlertTemplate.objects.get(alert_type=alert_type)
    except AlertTemplate.DoesNotExist:
        # Create default template
        templates = {
            'aqi_threshold': {
                'title_template': 'Air Quality Alert for {location}',
                'message_template': 'The air quality in {location} has reached {aqi} AQI ({pollutant}), which exceeds your threshold of {threshold}. Consider limiting outdoor activities.',
                'default_severity': 'medium'
            },
            'health_warning': {
                'title_template': 'Health Warning for {location}',
                'message_template': 'Based on your health conditions, the current air quality in {location} (AQI: {aqi}) may affect your health. Please take necessary precautions.',
                'default_severity': 'high'
            },
            'forecast_alert': {
                'title_template': 'Air Quality Forecast Alert for {location}',
                'message_template': 'Air quality in {location} is forecasted to reach unhealthy levels (AQI: {aqi}) in the coming hours.',
                'default_severity': 'medium'
            },
            'emergency': {
                'title_template': 'Emergency Air Quality Alert for {location}',
                'message_template': 'EMERGENCY: Air quality in {location} has reached hazardous levels (AQI: {aqi}). Avoid all outdoor activities and stay indoors.',
                'default_severity': 'critical'
            }
        }
        
        template_data = templates.get(alert_type, templates['aqi_threshold'])
        return AlertTemplate.objects.create(
            alert_type=alert_type,
            **template_data
        )


def send_alert_notifications(alert, health_profile):
    """Send alert notifications via configured channels"""
    user = alert.user
    notification_prefs = user.userprofile.notification_preferences
    
    # Email notification
    if notification_prefs in ['email', 'all'] and not alert.sent_via_email:
        send_email_notification(alert)
        alert.sent_via_email = True
    
    # SMS notification (placeholder)
    if notification_prefs in ['sms', 'all'] and not alert.sent_via_sms:
        send_sms_notification(alert)
        alert.sent_via_sms = True
    
    # Push notification (placeholder)
    if notification_prefs in ['push', 'all'] and not alert.sent_via_push:
        send_push_notification(alert)
        alert.sent_via_push = True
    
    alert.save()


def send_email_notification(alert):
    """Send email notification for alert"""
    try:
        user = alert.user
        
        # Render email template
        email_context = {
            'alert': alert,
            'user': user,
            'site_name': 'Air Quality Monitor',
        }
        
        html_message = render_to_string('health_alerts/email/alert_notification.html', email_context)
        plain_message = render_to_string('health_alerts/email/alert_notification.txt', email_context)
        
        send_mail(
            subject=f'Health Alert: {alert.title}',
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Email notification sent to {user.email} for alert {alert.id}")
        
    except Exception as e:
        logger.error(f"Error sending email notification: {e}")


def send_sms_notification(alert):
    """Send SMS notification for alert (placeholder)"""
    try:
        user = alert.user
        phone_number = user.userprofile.phone_number
        
        if not phone_number:
            logger.warning(f"No phone number for user {user.username}, skipping SMS")
            return
        
        # Placeholder SMS sending logic
        # In a real implementation, you would use services like:
        # - Twilio
        # - AWS SNS
        # - Firebase Cloud Messaging
        
        message = f"Health Alert: {alert.title}\n{alert.message[:100]}..."
        
        logger.info(f"SMS notification would be sent to {phone_number}: {message}")
        
    except Exception as e:
        logger.error(f"Error sending SMS notification: {e}")


def send_push_notification(alert):
    """Send push notification for alert (placeholder)"""
    try:
        user = alert.user
        
        # Placeholder push notification logic
        # In a real implementation, you would use services like:
        # - Firebase Cloud Messaging
        # - OneSignal
        # - Apple Push Notification Service
        
        notification_data = {
            'title': alert.title,
            'body': alert.message[:100] + '...' if len(alert.message) > 100 else alert.message,
            'icon': 'air_quality_alert',
            'click_action': f'/health-alerts/alerts/{alert.id}/',
            'data': {
                'alert_id': alert.id,
                'severity': alert.severity,
                'aqi_value': alert.aqi_value,
            }
        }
        
        logger.info(f"Push notification would be sent to {user.username}: {notification_data}")
        
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")


def check_and_create_alerts_for_location(location_name):
    """
    Check air quality for a location and create alerts for relevant users
    
    Args:
        location_name: Name of the location to check
    """
    try:
        # Get latest air quality reading for location
        latest_reading = AirQualityReading.objects.filter(
            location=location_name
        ).first()
        
        if not latest_reading:
            logger.warning(f"No air quality data available for {location_name}")
            return
        
        # Get users who have this location in their preferences
        user_locations = UserLocationPreference.objects.filter(
            location_name=location_name
        )
        
        for user_location in user_locations:
            user = user_location.user
            
            # Check if user has active health profile
            try:
                health_profile = UserHealthProfile.objects.get(user=user, is_active=True)
            except UserHealthProfile.DoesNotExist:
                continue
            
            # Create alert if needed
            create_health_alert(user, location_name, latest_reading)
            
    except Exception as e:
        logger.error(f"Error checking alerts for location {location_name}: {e}")


def cleanup_old_alerts(days_old=30):
    """
    Clean up old alerts to prevent database bloat
    
    Args:
        days_old: Delete alerts older than this many days
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_old)
        old_alerts = Alert.objects.filter(
            created_at__lt=cutoff_date,
            is_dismissed=True
        )
        
        count = old_alerts.count()
        old_alerts.delete()
        
        logger.info(f"Cleaned up {count} old alerts")
        
    except Exception as e:
        logger.error(f"Error cleaning up old alerts: {e}")


def get_alert_summary_for_user(user, days=7):
    """
    Get alert summary for user over specified period
    
    Args:
        user: User object
        days: Number of days to look back
        
    Returns:
        Dictionary with alert statistics
    """
    start_date = timezone.now() - timedelta(days=days)
    
    alerts = Alert.objects.filter(
        user=user,
        created_at__gte=start_date
    )
    
    return {
        'total_alerts': alerts.count(),
        'unread_alerts': alerts.filter(is_read=False).count(),
        'critical_alerts': alerts.filter(severity='critical').count(),
        'high_alerts': alerts.filter(severity='high').count(),
        'locations_alerted': alerts.values_list('location', flat=True).distinct().count(),
        'period_days': days
    }