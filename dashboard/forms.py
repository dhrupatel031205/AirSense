from django import forms
from .models import UserLocationPreference


class LocationPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserLocationPreference
        fields = ['location_name', 'latitude', 'longitude', 'is_primary', 'alert_threshold']
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'step': '0.000001'}),
            'alert_threshold': forms.NumberInput(attrs={'min': '0', 'max': '500'}),
        }
        help_texts = {
            'alert_threshold': 'AQI value above which you want to receive alerts (0-500)',
            'is_primary': 'Set as your primary location for main dashboard display',
        }