from django.contrib import admin
from .models import HealthCondition, UserHealthProfile, Alert, AlertTemplate


@admin.register(HealthCondition)
class HealthConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'aqi_threshold', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(UserHealthProfile)
class UserHealthProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'custom_threshold', 'alert_frequency', 'is_active')
    list_filter = ('alert_frequency', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('conditions',)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'alert_type', 'severity', 'location', 'aqi_value', 'is_read', 'created_at')
    list_filter = ('alert_type', 'severity', 'is_read', 'is_dismissed', 'created_at')
    search_fields = ('title', 'user__username', 'location', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(AlertTemplate)
class AlertTemplateAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'default_severity', 'is_active', 'created_at')
    list_filter = ('default_severity', 'is_active', 'created_at')
    search_fields = ('alert_type', 'title_template')