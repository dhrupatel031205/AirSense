from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def home(request):
    """Landing page view"""
    context = {
        'title': 'Air Quality Monitor',
        'description': 'Real-time air quality monitoring and health alerts for your community',
    }
    return render(request, 'landing/home.html', context)


def about(request):
    """About page view"""
    context = {
        'title': 'About Us',
        'description': 'Learn more about our mission to provide accurate air quality data',
    }
    return render(request, 'landing/about.html', context)


def features(request):
    """Features page view"""
    features_list = [
        {
            'title': 'Real-time Monitoring',
            'description': 'Get up-to-date air quality data for your location',
            'icon': 'monitor'
        },
        {
            'title': 'Health Alerts',
            'description': 'Personalized notifications based on your health conditions',
            'icon': 'health'
        },
        {
            'title': 'ML Predictions',
            'description': 'Advanced machine learning models for air quality forecasting',
            'icon': 'brain'
        },
        {
            'title': 'Community Action',
            'description': 'Join local environmental initiatives and policy recommendations',
            'icon': 'community'
        },
    ]
    
    context = {
        'title': 'Features',
        'features': features_list,
    }
    return render(request, 'landing/features.html', context)


@csrf_exempt
def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
            
            # TODO: Implement email sending logic
            # For now, just return success
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message! We will get back to you soon.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Sorry, there was an error sending your message. Please try again.'
            }, status=400)
    
    context = {
        'title': 'Contact Us',
    }
    return render(request, 'landing/contact.html', context)