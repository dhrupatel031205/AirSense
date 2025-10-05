from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg, Max, Min
from django.utils import timezone
from .models import (
    ScenarioTemplate, SimulationScenario, SimulationResult,
    ScenarioComparison, ImpactFactor
)
from .impact_engine import run_scenario_simulation, get_baseline_data
import json
import csv


def simulator_dashboard(request):
    """Main scenario simulator dashboard"""
    # Get popular templates
    popular_templates = ScenarioTemplate.objects.filter(
        is_public=True
    ).order_by('scenario_type')[:6]
    
    # User-specific data if logged in
    user_scenarios = None
    recent_results = None
    if request.user.is_authenticated:
        user_scenarios = SimulationScenario.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        recent_results = SimulationScenario.objects.filter(
            user=request.user,
            status='completed'
        ).order_by('-completed_at')[:3]
    
    context = {
        'title': 'Scenario Simulator',
        'popular_templates': popular_templates,
        'user_scenarios': user_scenarios,
        'recent_results': recent_results,
    }
    return render(request, 'scenario_simulator/dashboard.html', context)


def scenario_templates(request):
    """List of available scenario templates"""
    templates = ScenarioTemplate.objects.filter(is_public=True)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        templates = templates.filter(scenario_type=type_filter)
    
    # Filter by complexity
    complexity_filter = request.GET.get('complexity')
    if complexity_filter:
        templates = templates.filter(complexity_level=complexity_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        templates = templates.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'title': 'Scenario Templates',
        'templates': templates,
        'type_filter': type_filter,
        'complexity_filter': complexity_filter,
        'search_query': search_query,
        'scenario_types': ScenarioTemplate.SCENARIO_TYPES,
    }
    return render(request, 'scenario_simulator/templates.html', context)


def template_detail(request, template_id):
    """Template detail view"""
    template = get_object_or_404(ScenarioTemplate, id=template_id)
    
    # Get recent scenarios using this template
    recent_scenarios = SimulationScenario.objects.filter(
        template=template,
        is_public=True,
        status='completed'
    ).order_by('-completed_at')[:5]
    
    context = {
        'title': template.name,
        'template': template,
        'recent_scenarios': recent_scenarios,
    }
    return render(request, 'scenario_simulator/template_detail.html', context)


@login_required
def create_scenario(request):
    """Create a new simulation scenario"""
    if request.method == 'POST':
        # Handle form submission
        scenario = SimulationScenario(
            user=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            location=request.POST.get('location'),
            latitude=float(request.POST.get('latitude', 0)),
            longitude=float(request.POST.get('longitude', 0)),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            time_resolution=request.POST.get('time_resolution', 'hourly'),
        )
        
        # Parse parameters from form
        parameters = {}
        for key, value in request.POST.items():
            if key.startswith('param_'):
                param_name = key.replace('param_', '')
                try:
                    parameters[param_name] = float(value)
                except ValueError:
                    parameters[param_name] = value
        
        scenario.parameters = parameters
        scenario.save()
        
        messages.success(request, 'Scenario created successfully!')
        return redirect('scenario_simulator:scenario_detail', scenario_id=scenario.id)
    
    # Get available impact factors
    impact_factors = ImpactFactor.objects.filter(is_active=True)
    
    context = {
        'title': 'Create Scenario',
        'impact_factors': impact_factors,
    }
    return render(request, 'scenario_simulator/create.html', context)


@login_required
def create_from_template(request, template_id):
    """Create scenario from template"""
    template = get_object_or_404(ScenarioTemplate, id=template_id)
    
    if request.method == 'POST':
        scenario = SimulationScenario(
            user=request.user,
            template=template,
            name=request.POST.get('name', f"{template.name} - {timezone.now().strftime('%Y%m%d')}"),
            description=request.POST.get('description'),
            location=request.POST.get('location'),
            latitude=float(request.POST.get('latitude', 0)),
            longitude=float(request.POST.get('longitude', 0)),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            time_resolution=request.POST.get('time_resolution', 'hourly'),
        )
        
        # Start with template parameters and override with form data
        parameters = template.default_parameters.copy()
        for key, value in request.POST.items():
            if key.startswith('param_'):
                param_name = key.replace('param_', '')
                try:
                    parameters[param_name] = float(value)
                except ValueError:
                    parameters[param_name] = value
        
        scenario.parameters = parameters
        scenario.save()
        
        messages.success(request, f'Scenario created from template "{template.name}"!')
        return redirect('scenario_simulator:scenario_detail', scenario_id=scenario.id)
    
    context = {
        'title': f'Create from Template: {template.name}',
        'template': template,
    }
    return render(request, 'scenario_simulator/create_from_template.html', context)


@login_required
def my_scenarios(request):
    """List user's scenarios"""
    scenarios = SimulationScenario.objects.filter(user=request.user)
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        scenarios = scenarios.filter(status=status_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        scenarios = scenarios.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'title': 'My Scenarios',
        'scenarios': scenarios,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    return render(request, 'scenario_simulator/my_scenarios.html', context)


@login_required
def scenario_detail(request, scenario_id):
    """Scenario detail view"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    # Get summary statistics if completed
    summary_stats = None
    if scenario.status == 'completed' and scenario.result_points.exists():
        results = scenario.result_points.all()
        summary_stats = {
            'avg_aqi': results.aggregate(Avg('aqi_value'))['aqi_value__avg'],
            'max_aqi': results.aggregate(Max('aqi_value'))['aqi_value__max'],
            'min_aqi': results.aggregate(Min('aqi_value'))['aqi_value__min'],
            'data_points': results.count(),
        }
    
    context = {
        'title': scenario.name,
        'scenario': scenario,
        'summary_stats': summary_stats,
    }
    return render(request, 'scenario_simulator/detail.html', context)


@login_required
def run_simulation(request, scenario_id):
    """Run a simulation scenario"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    if scenario.status in ['running']:
        messages.warning(request, 'Simulation is already running!')
        return redirect('scenario_simulator:scenario_detail', scenario_id=scenario.id)
    
    if request.method == 'POST':
        # Start the simulation
        try:
            scenario.status = 'running'
            scenario.progress_percent = 0
            scenario.save()
            
            # Run simulation (this would typically be done asynchronously)
            success = run_scenario_simulation(scenario)
            
            if success:
                messages.success(request, 'Simulation completed successfully!')
            else:
                messages.error(request, 'Simulation failed. Please check the error log.')
                
        except Exception as e:
            scenario.status = 'failed'
            scenario.error_message = str(e)
            scenario.save()
            messages.error(request, f'Simulation failed: {e}')
        
        return redirect('scenario_simulator:scenario_detail', scenario_id=scenario.id)
    
    # Show confirmation page
    context = {
        'title': f'Run Simulation: {scenario.name}',
        'scenario': scenario,
    }
    return render(request, 'scenario_simulator/run_confirmation.html', context)


@login_required
def simulation_results(request, scenario_id):
    """View simulation results"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    if scenario.status != 'completed':
        messages.warning(request, 'Simulation is not yet completed!')
        return redirect('scenario_simulator:scenario_detail', scenario_id=scenario.id)
    
    # Get results data
    results = scenario.result_points.all().order_by('timestamp')
    
    # Prepare data for charts
    chart_data = {
        'timestamps': [r.timestamp.isoformat() for r in results],
        'aqi_values': [r.aqi_value for r in results],
        'pm25_values': [r.pm25_concentration for r in results if r.pm25_concentration],
        'baseline_aqi': [r.baseline_aqi for r in results if r.baseline_aqi],
    }
    
    context = {
        'title': f'Results: {scenario.name}',
        'scenario': scenario,
        'results': results[:100],  # Limit for display
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'scenario_simulator/results.html', context)


@login_required
def export_results(request, scenario_id):
    """Export simulation results as CSV"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    if scenario.status != 'completed':
        messages.error(request, 'Cannot export results from incomplete simulation!')
        return redirect('scenario_simulator:scenario_detail', scenario_id=scenario.id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{scenario.name}_results.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Timestamp', 'AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3',
        'Baseline AQI', 'Improvement %'
    ])
    
    for result in scenario.result_points.all():
        writer.writerow([
            result.timestamp,
            result.aqi_value,
            result.pm25_concentration,
            result.pm10_concentration,
            result.no2_concentration,
            result.so2_concentration,
            result.co_concentration,
            result.o3_concentration,
            result.baseline_aqi,
            result.improvement_percent,
        ])
    
    return response


@login_required
def delete_scenario(request, scenario_id):
    """Delete a scenario"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    if request.method == 'POST':
        scenario_name = scenario.name
        scenario.delete()
        messages.success(request, f'Scenario "{scenario_name}" deleted successfully!')
        return redirect('scenario_simulator:my_scenarios')
    
    context = {
        'title': f'Delete Scenario: {scenario.name}',
        'scenario': scenario,
    }
    return render(request, 'scenario_simulator/delete_confirmation.html', context)


@login_required
def clone_scenario(request, scenario_id):
    """Clone an existing scenario"""
    original_scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    # Create a clone
    clone = SimulationScenario(
        user=request.user,
        template=original_scenario.template,
        name=f"{original_scenario.name} (Copy)",
        description=original_scenario.description,
        location=original_scenario.location,
        latitude=original_scenario.latitude,
        longitude=original_scenario.longitude,
        parameters=original_scenario.parameters.copy(),
        start_date=original_scenario.start_date,
        end_date=original_scenario.end_date,
        time_resolution=original_scenario.time_resolution,
        is_public=False,  # Clones are private by default
    )
    clone.save()
    
    messages.success(request, f'Scenario cloned as "{clone.name}"!')
    return redirect('scenario_simulator:scenario_detail', scenario_id=clone.id)


@login_required
def create_comparison(request):
    """Create a comparison between scenarios"""
    user_scenarios = SimulationScenario.objects.filter(
        user=request.user,
        status='completed'
    )
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        selected_scenarios = request.POST.getlist('scenarios')
        
        comparison = ScenarioComparison.objects.create(
            user=request.user,
            name=name,
            description=description
        )
        
        for scenario_id in selected_scenarios:
            try:
                scenario = SimulationScenario.objects.get(id=scenario_id, user=request.user)
                comparison.scenarios.add(scenario)
            except SimulationScenario.DoesNotExist:
                pass
        
        messages.success(request, 'Comparison created successfully!')
        return redirect('scenario_simulator:comparison_detail', comparison_id=comparison.id)
    
    context = {
        'title': 'Create Comparison',
        'user_scenarios': user_scenarios,
    }
    return render(request, 'scenario_simulator/create_comparison.html', context)


@login_required
def my_comparisons(request):
    """List user's comparisons"""
    comparisons = ScenarioComparison.objects.filter(user=request.user)
    
    context = {
        'title': 'My Comparisons',
        'comparisons': comparisons,
    }
    return render(request, 'scenario_simulator/my_comparisons.html', context)


@login_required
def comparison_detail(request, comparison_id):
    """Comparison detail view"""
    comparison = get_object_or_404(ScenarioComparison, id=comparison_id, user=request.user)
    
    # Get comparison data for charts
    scenarios_data = []
    for scenario in comparison.scenarios.all():
        results = scenario.result_points.all().order_by('timestamp')
        scenarios_data.append({
            'name': scenario.name,
            'data': [{'x': r.timestamp.isoformat(), 'y': r.aqi_value} for r in results]
        })
    
    context = {
        'title': comparison.name,
        'comparison': comparison,
        'scenarios_data': json.dumps(scenarios_data),
    }
    return render(request, 'scenario_simulator/comparison_detail.html', context)


def public_scenarios(request):
    """List public scenarios"""
    scenarios = SimulationScenario.objects.filter(
        is_public=True,
        status='completed'
    ).order_by('-completed_at')
    
    # Filter by template type
    template_filter = request.GET.get('template')
    if template_filter:
        scenarios = scenarios.filter(template__scenario_type=template_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        scenarios = scenarios.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'title': 'Public Scenarios',
        'scenarios': scenarios,
        'template_filter': template_filter,
        'search_query': search_query,
    }
    return render(request, 'scenario_simulator/public_scenarios.html', context)


@login_required
def simulation_status_api(request, scenario_id):
    """API endpoint to get simulation status"""
    scenario = get_object_or_404(SimulationScenario, id=scenario_id, user=request.user)
    
    return JsonResponse({
        'status': scenario.status,
        'progress': scenario.progress_percent,
        'error_message': scenario.error_message,
        'updated_at': scenario.updated_at.isoformat(),
    })