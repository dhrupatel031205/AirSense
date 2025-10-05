from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Alert, UserHealthProfile, HealthCondition
from dashboard.models import UserLocationPreference, AirQualityReading


@login_required
def alerts_dashboard(request):
    """Main health alerts dashboard"""
    # Get user's recent alerts
    recent_alerts = Alert.objects.filter(user=request.user, is_dismissed=False)[:10]
    
    # Get current air quality for user's locations
    user_locations = UserLocationPreference.objects.filter(user=request.user)
    current_conditions = []
    
    for location in user_locations:
        latest_reading = AirQualityReading.objects.filter(
            location=location.location_name
        ).first()
        if latest_reading:
            current_conditions.append({
                'location': location,
                'reading': latest_reading,
                'needs_alert': latest_reading.aqi_value > location.alert_threshold
            })
    
    context = {
        'title': 'Health Alerts Dashboard',
        'recent_alerts': recent_alerts,
        'current_conditions': current_conditions,
        'unread_count': recent_alerts.filter(is_read=False).count(),
    }
    return render(request, 'health_alerts/dashboard.html', context)


@login_required
def health_profile(request):
    """Display user's health profile"""
    try:
        profile = UserHealthProfile.objects.get(user=request.user)
    except UserHealthProfile.DoesNotExist:
        profile = UserHealthProfile.objects.create(user=request.user)
    
    context = {
        'title': 'Health Profile',
        'profile': profile,
        'available_conditions': HealthCondition.objects.all(),
    }
    return render(request, 'health_alerts/profile.html', context)


@login_required
def edit_health_profile(request):
    """Edit user's health profile"""
    try:
        profile = UserHealthProfile.objects.get(user=request.user)
    except UserHealthProfile.DoesNotExist:
        profile = UserHealthProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update profile fields
        profile.age = request.POST.get('age') or None
        profile.custom_threshold = int(request.POST.get('custom_threshold', 100))
        profile.alert_frequency = request.POST.get('alert_frequency', 'immediate')
        
        # Update health conditions
        selected_conditions = request.POST.getlist('conditions')
        profile.conditions.clear()
        for condition_id in selected_conditions:
            try:
                condition = HealthCondition.objects.get(id=condition_id)
                profile.conditions.add(condition)
            except HealthCondition.DoesNotExist:
                pass
        
        profile.save()
        messages.success(request, 'Health profile updated successfully!')
        return redirect('health_alerts:profile')
    
    context = {
        'title': 'Edit Health Profile',
        'profile': profile,
        'available_conditions': HealthCondition.objects.all(),
    }
    return render(request, 'health_alerts/edit_profile.html', context)


@login_required
def alert_list(request):
    """Display list of user's alerts"""
    alerts = Alert.objects.filter(user=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter == 'unread':
        alerts = alerts.filter(is_read=False)
    elif status_filter == 'read':
        alerts = alerts.filter(is_read=True)
    elif status_filter == 'active':
        alerts = alerts.filter(is_dismissed=False)
    
    # Filter by severity
    severity_filter = request.GET.get('severity')
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    
    # Paginate results
    alerts = alerts[:50]  # Limit to 50 for now
    
    context = {
        'title': 'All Alerts',
        'alerts': alerts,
        'status_filter': status_filter,
        'severity_filter': severity_filter,
    }
    return render(request, 'health_alerts/list.html', context)


@login_required
def alert_detail(request, alert_id):
    """Display alert detail"""
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    
    # Mark as read
    if not alert.is_read:
        alert.is_read = True
        alert.save()
    
    context = {
        'title': f'Alert: {alert.title}',
        'alert': alert,
    }
    return render(request, 'health_alerts/detail.html', context)


@login_required
def dismiss_alert(request, alert_id):
    """Dismiss an alert"""
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    alert.is_dismissed = True
    alert.save()
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Alert dismissed successfully!')
    return redirect('health_alerts:list')


@login_required
def notification_settings(request):
    """Manage notification settings"""
    try:
        profile = UserHealthProfile.objects.get(user=request.user)
    except UserHealthProfile.DoesNotExist:
        profile = UserHealthProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        profile.alert_frequency = request.POST.get('alert_frequency', 'immediate')
        profile.is_active = 'notifications_enabled' in request.POST
        profile.save()
        
        # Update user profile notification preferences
        user_profile = request.user.userprofile
        user_profile.notification_preferences = request.POST.get('notification_method', 'email')
        user_profile.save()
        
        messages.success(request, 'Notification settings updated successfully!')
        return redirect('health_alerts:settings')
    
    context = {
        'title': 'Notification Settings',
        'profile': profile,
        'user_profile': request.user.userprofile,
    }
    return render(request, 'health_alerts/settings.html', context)


@login_required
def health_conditions(request):
    """Display available health conditions"""
    conditions = HealthCondition.objects.all().order_by('name')
    
    context = {
        'title': 'Health Conditions',
        'conditions': conditions,
    }
    return render(request, 'health_alerts/conditions.html', context)