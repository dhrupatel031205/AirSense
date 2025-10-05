from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.simple_tag
def aqi_progress_bar(aqi_value, width="100%"):
    """
    Renders an AQI progress bar with color coding
    """
    # Ensure aqi_value is a number
    try:
        aqi = float(aqi_value)
    except (ValueError, TypeError):
        aqi = 0
    
    # Calculate percentage (AQI max is typically 500)
    percentage = min((aqi / 500) * 100, 100)
    
    # Determine color based on AQI value
    if aqi <= 50:
        color = "#22c55e"  # Good - Green
        category = "Good"
    elif aqi <= 100:
        color = "#eab308"  # Moderate - Yellow
        category = "Moderate"
    elif aqi <= 150:
        color = "#f97316"  # Unhealthy for Sensitive - Orange
        category = "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        color = "#ef4444"  # Unhealthy - Red
        category = "Unhealthy"
    elif aqi <= 300:
        color = "#8b5cf6"  # Very Unhealthy - Purple
        category = "Very Unhealthy"
    else:
        color = "#7c2d12"  # Hazardous - Maroon
        category = "Hazardous"
    
    html = f"""
    <div class="aqi-meter" style="width: {width};">
        <div class="aqi-meter-fill" style="width: {percentage}%; background-color: {color};">
        </div>
    </div>
    <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>0</span>
        <span class="font-medium" style="color: {color};">{category}</span>
        <span>500+</span>
    </div>
    """
    
    return mark_safe(html)

@register.simple_tag
def aqi_color(aqi_value):
    """
    Returns the appropriate color for an AQI value
    """
    try:
        aqi = float(aqi_value)
    except (ValueError, TypeError):
        return "#6b7280"  # Gray for invalid values
    
    if aqi <= 50:
        return "#22c55e"  # Good - Green
    elif aqi <= 100:
        return "#eab308"  # Moderate - Yellow
    elif aqi <= 150:
        return "#f97316"  # Unhealthy for Sensitive - Orange
    elif aqi <= 200:
        return "#ef4444"  # Unhealthy - Red
    elif aqi <= 300:
        return "#8b5cf6"  # Very Unhealthy - Purple
    else:
        return "#7c2d12"  # Hazardous - Maroon

@register.simple_tag
def aqi_category(aqi_value):
    """
    Returns the AQI category name
    """
    try:
        aqi = float(aqi_value)
    except (ValueError, TypeError):
        return "Unknown"
    
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

@register.simple_tag
def aqi_health_message(aqi_value):
    """
    Returns health recommendation based on AQI
    """
    try:
        aqi = float(aqi_value)
    except (ValueError, TypeError):
        return "Unable to determine air quality status."
    
    if aqi <= 50:
        return "Air quality is satisfactory, and air pollution poses little or no risk."
    elif aqi <= 100:
        return "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
    elif aqi <= 150:
        return "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
    elif aqi <= 200:
        return "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
    elif aqi <= 300:
        return "Health alert: The risk of health effects is increased for everyone."
    else:
        return "Health warning of emergency conditions: everyone is more likely to be affected."

@register.simple_tag
def weather_icon(condition):
    """
    Returns appropriate weather icon class
    """
    condition = str(condition).lower()
    
    if 'clear' in condition or 'sunny' in condition:
        return 'fas fa-sun'
    elif 'cloud' in condition:
        return 'fas fa-cloud'
    elif 'rain' in condition:
        return 'fas fa-cloud-rain'
    elif 'snow' in condition:
        return 'fas fa-snowflake'
    elif 'storm' in condition or 'thunder' in condition:
        return 'fas fa-bolt'
    elif 'fog' in condition or 'mist' in condition:
        return 'fas fa-smog'
    else:
        return 'fas fa-cloud-sun'

@register.simple_tag
def format_number(value):
    """
    Format large numbers with K, M suffixes
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(int(num))

@register.filter
def multiply(value, arg):
    """
    Multiply filter for template calculations
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """
    Calculate percentage
    """
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.simple_tag
def json_script(value, element_id):
    """
    Output JSON data for JavaScript consumption
    """
    json_str = json.dumps(value)
    return mark_safe(f'<script id="{element_id}" type="application/json">{json_str}</script>')

@register.inclusion_tag('utils/aqi_badge.html')
def aqi_badge(aqi_value, size='normal'):
    """
    Render an AQI badge component
    """
    try:
        aqi = float(aqi_value)
    except (ValueError, TypeError):
        aqi = 0
    
    return {
        'aqi': aqi,
        'color': aqi_color(aqi),
        'category': aqi_category(aqi),
        'size': size
    }

@register.inclusion_tag('utils/location_card.html')
def location_card(location_data):
    """
    Render a location card with AQI data
    """
    return {
        'location': location_data
    }

@register.simple_tag
def current_year():
    """
    Return current year
    """
    from datetime import datetime
    return datetime.now().year

@register.simple_tag
def current_time():
    """
    Return current time
    """
    from datetime import datetime
    return datetime.now()

@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary in template
    """
    return dictionary.get(key)

@register.simple_tag(takes_context=True)
def active_nav(context, url_name):
    """
    Check if current URL matches the given URL name
    """
    request = context['request']
    try:
        return 'active' if request.resolver_match.url_name == url_name else ''
    except AttributeError:
        return ''

@register.simple_tag
def nasa_badge(text="NASA TEMPO"):
    """
    Render NASA badge
    """
    return mark_safe(f'<span class="nasa-badge"><i class="fas fa-satellite mr-1"></i>{text}</span>')