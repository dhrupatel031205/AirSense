# Air Quality Project

A comprehensive Django web application for monitoring air quality, health alerts, and environmental impact analysis.

## Features

- **User Authentication**: OAuth integration with Google, NASA, etc.
- **Real-time Dashboard**: Air quality monitoring with ML predictions
- **Health Alerts**: Personalized notifications for air quality changes
- **Eco Action**: Policy recommendations and environmental insights
- **Scenario Simulator**: What-if analysis for environmental changes
- **Social Impact**: Community engagement and environmental awareness

## Tech Stack

- **Backend**: Django 4.2+, Django REST Framework
- **Frontend**: Tailwind CSS
- **Database**: PostgreSQL
- **ML Models**: TensorFlow, Scikit-learn
- **APIs**: NASA TEMPO, Weather APIs
- **Task Queue**: Celery with Redis

## Quick Setup

### Option 1: Automated Setup (Recommended)
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. **Windows**: Run `start_system.bat` OR **Linux/Mac**: Run `./start_system.sh`

### Option 2: Manual Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure environment variables (optional)
6. Run migrations: `python manage.py migrate`
7. Initialize system: `python initialize_system.py`
8. Create superuser: `python manage.py createsuperuser`
9. Run development server: `python manage.py runserver`

### For Production with Background Tasks
1. Install Redis: `pip install redis` or use Docker
2. Start Celery worker: `celery -A airquality_project worker --loglevel=info`
3. Start Celery beat: `celery -A airquality_project beat --loglevel=info`

## Troubleshooting

### Quick Actions "Page Not Found" Error
The system automatically fixes URL routing. If you still see errors:
1. Run `python manage.py migrate`
2. Restart the server: `python manage.py runserver`

### ML Models Not Loading/Updating
The system includes automatic model initialization:
1. Run: `python manage.py update_predictions --initialize`
2. For regular updates: `python manage.py update_predictions`
3. Models will auto-train with available data

### No Predictions Showing
1. Initialize the system: `python initialize_system.py`
2. This creates sample data and trains models
3. Predictions update automatically every hour

### Demo Login
- Username: `demo`
- Password: `demo123`
- Or create your own account via the signup page

## Key Features Working

✅ **Dashboard**: Real-time air quality monitoring with ML predictions  
✅ **Quick Actions**: All 4 buttons (Simulator, Eco Tips, Community, Settings) working  
✅ **ML Predictions**: Auto-updating forecasts every hour  
✅ **Health Alerts**: Personalized recommendations based on air quality  
✅ **User Authentication**: OAuth with Google + local accounts  
✅ **Responsive Design**: Works on desktop and mobile  

## Project Structure

See the detailed folder structure in the project documentation.

## Management Commands

- `python manage.py update_predictions --initialize` - Initialize ML models
- `python manage.py update_predictions` - Update predictions for all locations
- `python manage.py update_predictions --location "New York, NY"` - Update specific location
- `python initialize_system.py` - Complete system setup

## License

MIT License