#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airquality_project.settings')
django.setup()

from scenario_simulator.models import ScenarioTemplate, ImpactFactor
from eco_action.models import EnvironmentalPolicy, CommunityAction, EcoTip, PolicyCategory
from social_impact.models import EnvironmentalChallenge
from django.contrib.auth.models import User

def create_scenario_templates():
    print("Creating scenario templates...")
    
    templates = [
        {
            'name': 'Traffic Reduction Initiative',
            'description': 'Simulate the impact of reducing vehicle traffic by implementing car-free zones and promoting public transport. Expected: Reduce PM2.5 by 15-25%, NO2 by 20-30%',
            'scenario_type': 'traffic',
            'complexity_level': 'intermediate',
            'default_parameters': {
                'traffic_reduction_percent': 30,
                'public_transport_increase': 25,
                'duration_days': 30
            }
        },
        {
            'name': 'Industrial Emission Controls',
            'description': 'Model stricter industrial emission standards and their effect on local air quality. Expected: Reduce SO2 by 35-45%, PM10 by 20-30%',
            'scenario_type': 'industrial',
            'complexity_level': 'advanced',
            'default_parameters': {
                'emission_reduction_percent': 40,
                'compliance_rate': 85,
                'implementation_months': 6
            }
        },
        {
            'name': 'Green Energy Transition',
            'description': 'Simulate replacing fossil fuel power plants with renewable energy sources. Expected: Reduce CO2 by 40-60%, SO2 by 50-70%',
            'scenario_type': 'policy',
            'complexity_level': 'advanced',
            'default_parameters': {
                'renewable_percent': 50,
                'coal_reduction': 60,
                'transition_years': 5
            }
        },
        {
            'name': 'Urban Forest Expansion',
            'description': 'Evaluate the air quality benefits of large-scale urban tree planting and green spaces. Expected: Reduce PM2.5 by 8-15%, improve O3 levels',
            'scenario_type': 'policy',
            'complexity_level': 'basic',
            'default_parameters': {
                'tree_coverage_increase': 20,
                'green_space_expansion': 15,
                'maintenance_years': 10
            }
        },
        {
            'name': 'Construction Dust Control',
            'description': 'Model the impact of strict construction site regulations on particulate matter. Expected: Reduce PM10 by 25-40% near construction zones',
            'scenario_type': 'industrial',
            'complexity_level': 'intermediate',
            'default_parameters': {
                'dust_suppression_efficiency': 70,
                'compliance_rate': 90,
                'active_sites_percent': 100
            }
        },
        {
            'name': 'Electric Vehicle Adoption',
            'description': 'Simulate widespread adoption of electric vehicles and charging infrastructure. Expected: Reduce NO2 by 30-45%, CO by 50-65%',
            'scenario_type': 'traffic',
            'complexity_level': 'intermediate',
            'default_parameters': {
                'ev_adoption_rate': 40,
                'charging_stations': 500,
                'years_to_target': 8
            }
        }
    ]
    
    for template_data in templates:
        template, created = ScenarioTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            print(f"  Created: {template.name}")

def create_impact_factors():
    print("Creating impact factors...")
    
    factors = [
        {'name': 'Traffic Volume', 'description': 'Vehicle density affecting NO2 and PM emissions', 'factor_type': 'transportation', 'no2_coefficient': 1.5, 'pm25_coefficient': 1.2},
        {'name': 'Industrial Emissions', 'description': 'Factory and plant emissions', 'factor_type': 'industrial', 'so2_coefficient': 2.0, 'pm10_coefficient': 1.8},
        {'name': 'Wind Speed', 'description': 'Wind dispersion effects', 'factor_type': 'weather_pattern', 'pm25_coefficient': 0.7, 'pm10_coefficient': 0.6},
        {'name': 'Temperature Inversion', 'description': 'Atmospheric temperature effects', 'factor_type': 'weather_pattern', 'pm25_coefficient': 1.4, 'o3_coefficient': 1.3},
        {'name': 'Wildfire Activity', 'description': 'Natural fire emissions', 'factor_type': 'natural', 'pm25_coefficient': 3.0, 'co_coefficient': 2.5},
        {'name': 'Construction Dust', 'description': 'Construction site particulate matter', 'factor_type': 'industrial', 'pm10_coefficient': 2.2, 'pm25_coefficient': 1.1}
    ]
    
    for factor_data in factors:
        factor, created = ImpactFactor.objects.get_or_create(
            name=factor_data['name'],
            defaults=factor_data
        )
        if created:
            print(f"  Created: {factor.name}")

def create_eco_action_data():
    print("Creating eco action data...")
    
    # Policy Categories
    categories = [
        {'name': 'Air Quality', 'description': 'Policies focused on improving air quality'},
        {'name': 'Transportation', 'description': 'Sustainable transportation initiatives'},
        {'name': 'Energy', 'description': 'Clean energy and efficiency policies'},
        {'name': 'Urban Planning', 'description': 'Sustainable city development'}
    ]
    
    for cat_data in categories:
        category, created = PolicyCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"  Created category: {category.name}")
    
    # Environmental Policies
    policies = [
        {
            'title': 'Clean Air Act Enhancement',
            'description': 'Strengthen emission standards for vehicles and industries to reduce air pollution by 30% over 5 years. Cost: $2.5M, Timeline: 18 months. Benefits: Reduce respiratory diseases by 25%, save $50M in healthcare costs.',
            'policy_type': 'national',
            'impact_level': 'high',
            'location': 'United States'
        },
        {
            'title': 'Electric Vehicle Incentive Program',
            'description': 'Provide tax credits and rebates for electric vehicle purchases and charging station installations. Cost: $1M, Timeline: 12 months. Benefits: Increase EV adoption by 40%, reduce transport emissions by 20%.',
            'policy_type': 'local',
            'impact_level': 'medium',
            'location': 'California'
        },
        {
            'title': 'Urban Green Space Initiative',
            'description': 'Mandate minimum green space requirements for new developments and retrofit existing areas. Cost: $800K, Timeline: 24 months. Benefits: Improve air quality, reduce urban heat island effect.',
            'policy_type': 'local',
            'impact_level': 'medium',
            'location': 'New York City'
        },
        {
            'title': 'Industrial Emission Monitoring',
            'description': 'Implement real-time monitoring systems for all major industrial facilities. Cost: $1.5M, Timeline: 15 months. Benefits: Ensure compliance, reduce industrial pollution by 35%.',
            'policy_type': 'regional',
            'impact_level': 'high',
            'location': 'Great Lakes Region'
        }
    ]
    
    air_quality_cat = PolicyCategory.objects.get(name='Air Quality')
    transport_cat = PolicyCategory.objects.get(name='Transportation')
    urban_cat = PolicyCategory.objects.get(name='Urban Planning')
    
    policy_categories = [air_quality_cat, transport_cat, urban_cat, air_quality_cat]
    
    for i, policy_data in enumerate(policies):
        policy_data['category'] = policy_categories[i]
        policy, created = EnvironmentalPolicy.objects.get_or_create(
            title=policy_data['title'],
            defaults=policy_data
        )
        if created:
            print(f"  Created policy: {policy.title}")
    
    # Community Actions
    from django.utils import timezone
    from datetime import timedelta
    
    # Get demo user as organizer
    try:
        demo_user = User.objects.get(username='demo')
    except User.DoesNotExist:
        demo_user = User.objects.create_user('demo', 'demo@test.com', 'demo123')
    
    actions = [
        {
            'title': 'Community Tree Planting Day',
            'description': 'Join neighbors to plant 500 trees in local parks and streets to improve air quality. Expected impact: Plant 500 trees, improve local air quality.',
            'action_type': 'tree_planting',
            'location': 'Central Park, New York',
            'organizer': demo_user,
            'max_participants': 100,
            'start_date': timezone.now() + timedelta(days=7),
            'status': 'active'
        },
        {
            'title': 'Car-Free Sunday Initiative',
            'description': 'Monthly car-free events in downtown area to promote cycling and walking. Expected impact: Reduce traffic emissions by 60% on event days.',
            'action_type': 'awareness',
            'location': 'Downtown Los Angeles',
            'organizer': demo_user,
            'max_participants': 500,
            'start_date': timezone.now() + timedelta(days=14),
            'status': 'planning'
        },
        {
            'title': 'Air Quality Monitoring Workshop',
            'description': 'Learn to use portable air quality sensors and contribute to community data collection. Expected impact: Train 50 community monitors, expand data coverage.',
            'action_type': 'monitoring',
            'location': 'Chicago Community Center',
            'organizer': demo_user,
            'max_participants': 50,
            'start_date': timezone.now() + timedelta(days=21),
            'status': 'active'
        }
    ]
    
    for action_data in actions:
        action, created = CommunityAction.objects.get_or_create(
            title=action_data['title'],
            defaults=action_data
        )
        if created:
            print(f"  Created action: {action.title}")
    
    # Eco Tips
    tips = [
        {
            'title': 'Use Public Transportation',
            'content': 'Taking public transport instead of driving can reduce your carbon footprint by up to 45%. Plan your routes using transit apps.',
            'category': 'transport',
            'difficulty_level': 'easy',
            'estimated_impact': 'Reduce personal CO2 by 2.3 tons/year',
            'is_featured': True
        },
        {
            'title': 'Plant Indoor Air-Purifying Plants',
            'content': 'Spider plants, peace lilies, and snake plants naturally filter indoor air pollutants. Place 2-3 plants per room.',
            'category': 'indoor',
            'difficulty_level': 'easy',
            'estimated_impact': 'Improve indoor air quality by 15-20%',
            'is_featured': True
        },
        {
            'title': 'Switch to LED Lighting',
            'content': 'LED bulbs use 75% less energy and last 25 times longer than incandescent bulbs, reducing power plant emissions.',
            'category': 'energy',
            'difficulty_level': 'easy',
            'estimated_impact': 'Save 80% on lighting energy costs'
        },
        {
            'title': 'Start Composting',
            'content': 'Composting organic waste reduces methane emissions from landfills and creates nutrient-rich soil for plants.',
            'category': 'waste',
            'difficulty_level': 'medium',
            'estimated_impact': 'Reduce household waste by 30%'
        }
    ]
    
    for tip_data in tips:
        tip, created = EcoTip.objects.get_or_create(
            title=tip_data['title'],
            defaults=tip_data
        )
        if created:
            print(f"  Created tip: {tip.title}")

def create_social_challenges():
    print("Creating environmental challenges...")
    
    from django.utils import timezone
    from datetime import timedelta, date
    
    # Get demo user as creator
    try:
        demo_user = User.objects.get(username='demo')
    except User.DoesNotExist:
        demo_user = User.objects.create_user('demo', 'demo@test.com', 'demo123')
    
    challenges = [
        {
            'title': '30-Day Air Quality Champion',
            'description': 'Take daily actions to improve air quality and track your impact over 30 days.',
            'challenge_type': 'action',
            'difficulty': 'medium',
            'duration_days': 30,
            'points_reward': 500,
            'requirements': 'Complete 3 air-friendly actions daily: use public transport, check air quality, avoid outdoor exercise during high pollution',
            'creator': demo_user,
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=30)
        },
        {
            'title': 'Community Clean Air Week',
            'description': 'Organize neighborhood activities to raise awareness about air pollution and solutions.',
            'challenge_type': 'awareness',
            'difficulty': 'hard',
            'duration_days': 7,
            'points_reward': 1000,
            'requirements': 'Organize 2+ community events, engage 20+ neighbors, document activities with photos',
            'creator': demo_user,
            'start_date': date.today() + timedelta(days=7),
            'end_date': date.today() + timedelta(days=14)
        },
        {
            'title': 'Green Commute Challenge',
            'description': 'Switch to eco-friendly transportation for one month and inspire others.',
            'challenge_type': 'reduction',
            'difficulty': 'easy',
            'duration_days': 30,
            'points_reward': 300,
            'requirements': 'Use public transport, bike, or walk for 80% of trips. Share your experience weekly.',
            'creator': demo_user,
            'start_date': date.today() + timedelta(days=14),
            'end_date': date.today() + timedelta(days=44)
        }
    ]
    
    for challenge_data in challenges:
        challenge, created = EnvironmentalChallenge.objects.get_or_create(
            title=challenge_data['title'],
            defaults=challenge_data
        )
        if created:
            print(f"  Created challenge: {challenge.title}")

def main():
    print("Creating comprehensive scenario and eco action data...")
    create_scenario_templates()
    create_impact_factors()
    create_eco_action_data()
    create_social_challenges()
    print("Data creation completed!")

if __name__ == '__main__':
    main()