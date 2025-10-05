# Repository Cheat Sheet

## Project Summary
- **Name**: Air Quality Project (Django-based web platform)
- **Purpose**: Monitor air quality, provide health alerts, simulate scenarios, and support eco-action insights
- **Key Apps**: `landing`, `dashboard`, `health_alerts`, `eco_action`, `scenario_simulator`, `social_impact`, `users`, `utils`

## Tech Stack
- **Backend**: Django 4.2+, Django REST Framework
- **Frontend**: Tailwind CSS with custom static assets (CSS/JS)
- **Database**: SQLite for local development (configured via `db.sqlite3`)
- **Task Queue**: Celery with Redis (as referenced in docs)
- **APIs / External**: NASA TEMPO, Weather APIs

## Directory Highlights
- `manage.py`: Django entry point
- `airquality_project/`: Global project settings and URL routing
- `landing/`: Marketing landing pages, hero sections, navbar
- `dashboard/`: Real-time air quality dashboards
- `health_alerts/`: Alerts, notifications, templates/static for alerts
- `eco_action/`: Policy recommendation logic and pages
- `scenario_simulator/`: Environmental simulation engine & UI
- `social_impact/`: Community engagement features
- `users/`: Authentication, OAuth, profiles
- `utils/`: Shared utilities, template tags, helpers
- `templates/`: Base templates and shared components
- `static/`: Global CSS/JS assets (Tailwind, theme overrides)
- `media/`: Upload storage placeholder
- `requirements.txt`: Python dependencies

## Frontend Entry Points
- `templates/base.html`: Global layout, navbar, CSS/JS inclusion
- `static/css/theme.css`, `static/css/tailwind.css`: Core styles
- `landing/templates/landing/*.html`: Landing page sections
- `landing/static/landing`: Landing-specific assets
- `static/js/main.js`: Global JavaScript behavior

## Common Commands
```bash
# Create & activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations & run server
python manage.py migrate
python manage.py runserver

# Collect static files
python manage.py collectstatic
```

## Testing & Quality
- No dedicated automated tests found in repo.
- Manual testing recommended via Django development server.

## Contribution Tips
- Follow Django app conventions.
- Keep styles consistent with Tailwind setup.
- Use reusable components/templates where possible.
- Update `README.md` or related docs when adding major features.