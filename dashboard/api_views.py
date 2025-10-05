from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ml_models.ml_manager import MLModelManager
import json

@csrf_exempt
def health_chat(request):
    """Health chatbot API endpoint"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        
        if not question:
            return JsonResponse({'error': 'Question is required'}, status=400)
        
        # Get user profile for personalized responses (support guest users)
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_profile = {
                'age': getattr(request.user, 'age', 30),
                'conditions': []  # Would come from user health profile
            }
        else:
            # Guest/default profile
            user_profile = {
                'age': 30,
                'conditions': []
            }
        
        # Get current AQI (mock for now)
        current_aqi = 73

        # Use ML manager for chatbot response
        ml_manager = MLModelManager()
        # Allow the ML chatbot to answer for guests as well (limited personalization)
        response = ml_manager.chat_response(question, user_profile, current_aqi)

        return JsonResponse({
            'response': response.get('message', get_fallback_response(question)),
            'confidence': response.get('confidence', 0.8)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_fallback_response(question):
    """Fallback responses when ML chatbot is not available"""
    question_lower = question.lower()
    
    responses = {
        'asthma': 'For people with asthma, limit outdoor activities when AQI is above 100. Keep your inhaler handy and consider indoor exercises.',
        'exercise': 'Best times for outdoor exercise are early morning (6-8 AM) when air quality is typically better. Avoid exercising outdoors when AQI exceeds 150.',
        'children': 'Children are more sensitive to air pollution. Limit outdoor play when AQI is above 100 and ensure they stay hydrated.',
        'mask': 'N95 or P100 masks can help filter particles when AQI is high. Make sure the mask fits properly for maximum protection.',
        'symptoms': 'Common symptoms of poor air quality include coughing, throat irritation, and eye irritation. If symptoms persist, consult a healthcare provider.',
        'pregnancy': 'Pregnant women should be extra cautious about air quality. Stay indoors when AQI is above 100 and use air purifiers if available.',
        'elderly': 'Older adults are at higher risk from air pollution. Monitor air quality closely and limit outdoor activities during poor air quality days.',
        'heart': 'People with heart conditions should avoid outdoor activities when AQI exceeds 100. Consult your doctor about air quality precautions.',
        'indoor': 'To improve indoor air quality: use air purifiers, keep windows closed during high pollution, and avoid smoking indoors.',
        'plants': 'Some indoor plants like spider plants, peace lilies, and snake plants can help improve indoor air quality naturally.'
    }
    
    for keyword, response in responses.items():
        if keyword in question_lower:
            return response
    
    return "I can help with air quality health questions. Try asking about asthma, exercise, children's health, masks, symptoms, or indoor air quality."

@csrf_exempt
def ml_predictions(request):
    """Get ML predictions for a location"""
    if request.method == 'GET':
        location = request.GET.get('location', 'New York, NY')
        
        try:
            ml_manager = MLModelManager()
            
            # Mock location data
            location_data = {
                'location': location,
                'aqi': 73,
                'pm25': 25,
                'pm10': 35,
                'no2': 45,
                'o3': 55,
                'temperature': 24,
                'humidity': 65,
                'wind_speed': 15
            }
            
            predictions = ml_manager.get_real_time_predictions(location_data)
            
            return JsonResponse({
                'location': location,
                'predictions': predictions,
                'status': 'success'
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    return JsonResponse({'error': 'GET method required'}, status=405)

@csrf_exempt
def scenario_simulation(request):
    """Run scenario simulation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            scenario_type = data.get('scenario_type', 'traffic_reduction')
            parameters = data.get('parameters', {})
            
            ml_manager = MLModelManager()
            
            # Mock baseline data
            baseline_data = {
                'location': data.get('location', 'New York, NY'),
                'current_aqi': 73,
                'pm25': 25,
                'pm10': 35,
                'no2': 45,
                'o3': 55
            }
            
            # Run scenario analysis
            scenarios = {scenario_type: parameters}
            results = ml_manager.run_scenario_analysis(baseline_data, scenarios)
            
            return JsonResponse({
                'scenario_type': scenario_type,
                'results': results,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'status': 'error'
            }, status=500)
    
    return JsonResponse({'error': 'POST method required'}, status=405)


def anomalies(request):
    """Return anomaly detection results for a given location (GET)
    Expects query param 'location'."""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)

    location = request.GET.get('location', 'New York, NY')

    try:
        ml_manager = MLModelManager()

        # Mock location data similar to ml_predictions
        location_data = {
            'location': location,
            'aqi': 73,
            'pm25': 25,
            'pm10': 35,
            'no2': 45,
            'o3': 55,
            'temperature': 24,
            'humidity': 65,
            'wind_speed': 15
        }

        # Use manager to get anomaly info (it will include 'anomaly_status' when available)
        results = ml_manager.get_real_time_predictions(location_data)

        anomaly_status = results.get('anomaly_status') if isinstance(results, dict) else None

        return JsonResponse({
            'location': location,
            'anomaly_status': anomaly_status,
            'models_trained': ml_manager.get_model_status().get('models_trained', {})
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)