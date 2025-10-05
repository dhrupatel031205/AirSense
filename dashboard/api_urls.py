from django.urls import path
from . import api_views

app_name = 'dashboard_api'

urlpatterns = [
    path('predictions/', api_views.ml_predictions, name='ml_predictions'),
    path('scenarios/', api_views.scenario_simulation, name='scenario_simulation'),
    path('anomalies/', api_views.anomalies, name='anomalies'),
    path('chat/', api_views.health_chat, name='health_chat'),
]
