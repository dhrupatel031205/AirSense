#!/bin/bash

echo "🚀 Starting AirSense System..."
echo

echo "📊 Initializing system (first time setup)..."
python initialize_system.py
echo

echo "🌐 Starting Django development server..."
echo "Visit http://127.0.0.1:8000/ in your browser"
echo "Press Ctrl+C to stop the server"
echo

python manage.py runserver