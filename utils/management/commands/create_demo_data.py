# Management command to populate demo data

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from dashboard.models import AirQualityReading, UserLocationPreference, MLPrediction
from health_alerts.models import UserHealthProfile, HealthCondition, Alert
from eco_action.models import EnvironmentalPolicy, PolicyCategory, CommunityAction, EcoTip
from scenario_simulator.models import ScenarioTemplate, ImpactFactor
from social_impact.models import UserSocialProfile, EnvironmentalChallenge


class Command(BaseCommand):
    help = 'Populate database with demo data for EcoSky'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating demo data for EcoSky...'))
        
        # Create demo users
        self.create_demo_users()
        
        # Create air quality data
        self.create_air_quality_data()
        
        # Create health conditions
        self.create_health_conditions()
        
        # Create policy categories and policies
        self.create_policy_data()
        
        # Create eco tips
        self.create_eco_tips()
        
        # Create scenario templates
        self.create_scenario_templates()
        
        # Create environmental challenges
        self.create_environmental_challenges()
        
        # Create impact factors
        self.create_impact_factors()
        
        self.stdout.write(self.style.SUCCESS('Demo data created successfully!'))
    
    def create_demo_users(self):
        """Create demo users with profiles"""
        users_data = [
            {
                'username': 'demo_user',
                'email': 'demo@ecosky.com',
                'first_name': 'Demo',
                'last_name': 'User',
                'password': 'demo_password'
            },
            {
                'username': 'dr_smith',
                'email': 'sarah.smith@hospital.com',
                'first_name': 'Sarah',
                'last_name': 'Smith',
                'password': 'health_worker_pass'
            },
            {
                'username': 'student_mike',
                'email': 'mike.student@university.edu',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'password': 'student_pass'
            }
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                
                # Create user location preferences
                locations = [
                    ('Home', 40.7128, -74.0060, True),
                    ('Office', 40.7589, -73.9851, False),
                    ('Gym', 40.7282, -74.0776, False)
                ]
                
                for name, lat, lng, is_primary in locations:
                    UserLocationPreference.objects.get_or_create(
                        user=user,
                        location_name=name,
                        defaults={
                            'latitude': lat,
                            'longitude': lng,
                            'is_primary': is_primary,
                            'alert_threshold': random.randint(75, 125)
                        }
                    )
                
                # Create health profile
                UserHealthProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'custom_threshold': random.randint(75, 100),
                        'alert_frequency': random.choice(['immediate', 'hourly', 'daily']),
                        'is_active': True
                    }
                )
                
                # Create social profile
                UserSocialProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': f'EcoSky user passionate about clean air and environmental action.',
                        'location': 'New York City',
                        'total_points': random.randint(100, 1000),
                        'posts_count': random.randint(0, 25),
                        'challenges_completed': random.randint(0, 10),
                        'reports_submitted': random.randint(0, 15)
                    }
                )
                
                self.stdout.write(f'Created user: {user.username}')
    
    def create_air_quality_data(self):
        """Create sample air quality readings"""
        locations = [
            ('New York City', 40.7128, -74.0060),
            ('Los Angeles', 34.0522, -118.2437),
            ('Chicago', 41.8781, -87.6298),
            ('Houston', 29.7604, -95.3698),
            ('Phoenix', 33.4484, -112.0740)
        ]
        
        pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
        
        # Create readings for the last 7 days
        for i in range(7):
            date = timezone.now() - timedelta(days=i)
            
            for location_name, lat, lng in locations:
                for pollutant in pollutants:
                    # Generate realistic AQI values
                    base_aqi = random.randint(25, 150)
                    concentration = self.aqi_to_concentration(base_aqi, pollutant)
                    
                    AirQualityReading.objects.get_or_create(
                        location=location_name,
                        latitude=lat,
                        longitude=lng,
                        pollutant_type=pollutant,
                        timestamp=date,
                        defaults={
                            'concentration': concentration,
                            'aqi_value': base_aqi,
                            'source': 'NASA TEMPO' if random.random() > 0.3 else 'Ground Sensor'
                        }
                    )
        
        self.stdout.write('Created air quality readings')
    
    def create_health_conditions(self):
        """Create health conditions"""
        conditions_data = [
            ('Asthma', 'Chronic respiratory condition affecting airways', 75),
            ('COPD', 'Chronic obstructive pulmonary disease', 50),
            ('Heart Disease', 'Cardiovascular conditions', 100),
            ('Diabetes', 'Blood sugar regulation disorder', 100),
            ('Allergies', 'Environmental allergic reactions', 75),
            ('Pregnancy', 'Expecting mothers', 75)
        ]
        
        for name, description, threshold in conditions_data:
            HealthCondition.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'aqi_threshold': threshold
                }
            )
        
        self.stdout.write('Created health conditions')
    
    def create_policy_data(self):
        """Create policy categories and policies"""
        categories_data = [
            ('Transportation', 'Vehicle emissions and transportation policies'),
            ('Industrial', 'Industrial emission regulations'),
            ('Energy', 'Clean energy and power generation'),
            ('Urban Planning', 'City design and green spaces'),
            ('Agriculture', 'Farming and land use policies')
        ]
        
        for name, description in categories_data:
            category, created = PolicyCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            
            if created:
                # Create sample policies for each category
                policies = [
                    f'Clean {name} Initiative 2024',
                    f'{name} Emission Reduction Act',
                    f'Sustainable {name} Development Plan'
                ]
                
                for policy_title in policies:
                    EnvironmentalPolicy.objects.get_or_create(
                        title=policy_title,
                        defaults={
                            'description': f'Comprehensive policy addressing {name.lower()} environmental impacts.',
                            'category': category,
                            'policy_type': random.choice(['local', 'regional', 'national']),
                            'impact_level': random.choice(['low', 'medium', 'high']),
                            'location': random.choice(['New York', 'California', 'National'])
                        }
                    )
        
        self.stdout.write('Created policy data')
    
    def create_eco_tips(self):
        """Create eco-friendly tips"""
        tips_data = [
            ('Use Public Transportation', 'Take buses, trains, or subways instead of driving alone to reduce emissions.', 'transport', 'easy'),
            ('Plant Indoor Plants', 'Add air-purifying plants like snake plants or pothos to your home.', 'indoor', 'easy'),
            ('Reduce Energy Use', 'Turn off lights and unplug devices when not in use to reduce power plant emissions.', 'energy', 'easy'),
            ('Bike to Work', 'Cycle instead of driving for short commutes to improve air quality.', 'transport', 'medium'),
            ('Support Clean Energy', 'Choose renewable energy options for your home electricity.', 'energy', 'medium'),
            ('Reduce Meat Consumption', 'Eat less meat to reduce methane emissions from agriculture.', 'health', 'medium'),
        ]
        
        for title, content, category, difficulty in tips_data:
            EcoTip.objects.get_or_create(
                title=title,
                defaults={
                    'content': content,
                    'category': category,
                    'difficulty_level': difficulty,
                    'estimated_impact': f'Reduces carbon footprint by {random.randint(5, 25)}%',
                    'is_featured': random.random() > 0.7
                }
            )
        
        self.stdout.write('Created eco tips')
    
    def create_scenario_templates(self):
        """Create scenario simulation templates"""
        templates_data = [
            {
                'name': 'Traffic Reduction Scenario',
                'description': 'Simulate the impact of reducing vehicle traffic by various percentages',
                'scenario_type': 'traffic',
                'complexity_level': 'basic',
                'parameters': {
                    'traffic_reduction': 25,
                    'public_transport_increase': 15,
                    'bike_usage_increase': 10
                }
            },
            {
                'name': 'Industrial Emission Control',
                'description': 'Model the effects of stricter industrial emission standards',
                'scenario_type': 'industrial',
                'complexity_level': 'intermediate',
                'parameters': {
                    'emission_reduction': 30,
                    'renewable_energy': 40,
                    'efficiency_improvement': 20
                }
            },
            {
                'name': 'Wildfire Impact Assessment',
                'description': 'Assess air quality impact during wildfire events',
                'scenario_type': 'wildfire',
                'complexity_level': 'advanced',
                'parameters': {
                    'fire_intensity': 50,
                    'wind_speed': 15,
                    'duration_hours': 72
                }
            }
        ]
        
        for template_data in templates_data:
            ScenarioTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    'description': template_data['description'],
                    'scenario_type': template_data['scenario_type'],
                    'complexity_level': template_data['complexity_level'],
                    'default_parameters': template_data['parameters'],
                    'is_public': True
                }
            )
        
        self.stdout.write('Created scenario templates')
    
    def create_environmental_challenges(self):
        """Create environmental challenges"""
        challenges_data = [
            {
                'title': 'Car-Free Week Challenge',
                'description': 'Avoid using personal vehicles for one week',
                'challenge_type': 'reduction',
                'difficulty': 'medium',
                'duration_days': 7,
                'points_reward': 100,
                'requirements': 'Use only public transport, walking, or cycling for one week'
            },
            {
                'title': 'Energy Saver Month',
                'description': 'Reduce home energy consumption by 20%',
                'challenge_type': 'reduction',
                'difficulty': 'easy',
                'duration_days': 30,
                'points_reward': 150,
                'requirements': 'Monitor and reduce electricity usage by at least 20%'
            },
            {
                'title': 'Air Quality Ambassador',
                'description': 'Share air quality information with 5 friends',
                'challenge_type': 'awareness',
                'difficulty': 'easy',
                'duration_days': 14,
                'points_reward': 75,
                'requirements': 'Educate 5 people about air quality and EcoSky'
            }
        ]
        
        for challenge_data in challenges_data:
            start_date = timezone.now().date()
            end_date = start_date + timedelta(days=challenge_data['duration_days'])
            
            EnvironmentalChallenge.objects.get_or_create(
                title=challenge_data['title'],
                defaults={
                    'description': challenge_data['description'],
                    'challenge_type': challenge_data['challenge_type'],
                    'difficulty': challenge_data['difficulty'],
                    'duration_days': challenge_data['duration_days'],
                    'points_reward': challenge_data['points_reward'],
                    'requirements': challenge_data['requirements'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'creator': User.objects.first(),
                    'is_active': True,
                    'is_featured': random.random() > 0.5
                }
            )
        
        self.stdout.write('Created environmental challenges')
    
    def create_impact_factors(self):
        """Create impact factors for simulations"""
        factors_data = [
            {
                'name': 'Vehicle Traffic',
                'description': 'Impact of road vehicle emissions',
                'factor_type': 'transportation',
                'pm25_coefficient': 1.3,
                'no2_coefficient': 1.5,
                'co_coefficient': 1.4
            },
            {
                'name': 'Industrial Emissions',
                'description': 'Pollution from industrial facilities',
                'factor_type': 'industrial',
                'pm25_coefficient': 1.8,
                'so2_coefficient': 2.0,
                'no2_coefficient': 1.6
            },
            {
                'name': 'Wind Speed',
                'description': 'Effect of wind on pollutant dispersion',
                'factor_type': 'weather_pattern',
                'pm25_coefficient': 0.7,
                'pm10_coefficient': 0.6,
                'no2_coefficient': 0.8
            }
        ]
        
        for factor_data in factors_data:
            ImpactFactor.objects.get_or_create(
                name=factor_data['name'],
                defaults=factor_data
            )
        
        self.stdout.write('Created impact factors')
    
    def aqi_to_concentration(self, aqi, pollutant_type):
        """Convert AQI to approximate concentration"""
        if pollutant_type == 'PM2.5':
            return aqi * 0.4  # Rough approximation
        elif pollutant_type == 'PM10':
            return aqi * 0.8
        elif pollutant_type == 'NO2':
            return aqi * 1.2
        elif pollutant_type == 'SO2':
            return aqi * 0.3
        elif pollutant_type == 'CO':
            return aqi * 0.1
        elif pollutant_type == 'O3':
            return aqi * 1.0
        return aqi * 0.5