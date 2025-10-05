from django.urls import path
from . import views

app_name = 'scenario_simulator'

urlpatterns = [
    path('', views.simulator_dashboard, name='dashboard'),
    path('templates/', views.scenario_templates, name='templates'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    path('create/', views.create_scenario, name='create'),
    path('create/from-template/<int:template_id>/', views.create_from_template, name='create_from_template'),
    path('scenarios/', views.my_scenarios, name='my_scenarios'),
    path('scenarios/<int:scenario_id>/', views.scenario_detail, name='scenario_detail'),
    path('scenarios/<int:scenario_id>/run/', views.run_simulation, name='run_simulation'),
    path('scenarios/<int:scenario_id>/results/', views.simulation_results, name='results'),
    path('scenarios/<int:scenario_id>/export/', views.export_results, name='export_results'),
    path('scenarios/<int:scenario_id>/delete/', views.delete_scenario, name='delete_scenario'),
    path('scenarios/<int:scenario_id>/clone/', views.clone_scenario, name='clone_scenario'),
    path('compare/', views.create_comparison, name='create_comparison'),
    path('comparisons/', views.my_comparisons, name='my_comparisons'),
    path('comparisons/<int:comparison_id>/', views.comparison_detail, name='comparison_detail'),
    path('public/', views.public_scenarios, name='public_scenarios'),
    path('api/simulation-status/<int:scenario_id>/', views.simulation_status_api, name='simulation_status'),
]