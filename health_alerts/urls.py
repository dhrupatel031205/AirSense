from django.urls import path
from . import views

app_name = 'health_alerts'

urlpatterns = [
    path('', views.alerts_dashboard, name='dashboard'),
    path('profile/', views.health_profile, name='profile'),
    path('profile/edit/', views.edit_health_profile, name='edit_profile'),
    path('alerts/', views.alert_list, name='list'),
    path('alerts/<int:alert_id>/', views.alert_detail, name='detail'),
    path('alerts/<int:alert_id>/dismiss/', views.dismiss_alert, name='dismiss'),
    path('settings/', views.notification_settings, name='settings'),
    path('conditions/', views.health_conditions, name='conditions'),
]