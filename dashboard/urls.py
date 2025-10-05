from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

app_name = 'dashboard'

# API routes for REST framework
router = DefaultRouter()
router.register(r'air-quality', views.AirQualityReadingViewSet)
router.register(r'predictions', views.MLPredictionViewSet)

urlpatterns = [
    # Web views
    path('', views.dashboard_home, name='home'),
    path('monitoring/', views.air_quality_monitoring, name='monitoring'),
    path('predictions/', views.ml_predictions, name='predictions'),
    path('locations/', views.user_locations, name='locations'),
    path('locations/add/', views.add_location, name='add_location'),
    path('locations/<int:location_id>/delete/', views.delete_location, name='delete_location'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/current-aqi/<str:location>/', views.get_current_aqi, name='current_aqi'),
    path('api/forecast/<str:location>/', views.get_forecast, name='forecast'),
    
    # ML API endpoints
    path('api/ml/predictions/', api_views.ml_predictions, name='ml_predictions'),
    path('api/ml/scenarios/', api_views.scenario_simulation, name='scenario_simulation'),
    path('api/ml/anomalies/', api_views.anomalies, name='anomalies'),
    path('api/ml/chat/', api_views.health_chat, name='health_chat'),
]