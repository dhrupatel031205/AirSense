from django.contrib import admin
from .models import ScenarioTemplate, SimulationScenario, SimulationResult, ScenarioComparison, ImpactFactor


@admin.register(ScenarioTemplate)
class ScenarioTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'scenario_type', 'complexity_level', 'is_public', 'created_by', 'created_at')
    list_filter = ('scenario_type', 'complexity_level', 'is_public', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(SimulationScenario)
class SimulationScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'template', 'location', 'status', 'progress_percent', 'created_at')
    list_filter = ('status', 'template__scenario_type', 'is_public', 'created_at')
    search_fields = ('name', 'description', 'location', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('progress_percent', 'completed_at')


@admin.register(SimulationResult)
class SimulationResultAdmin(admin.ModelAdmin):
    list_display = ('scenario', 'timestamp', 'aqi_value', 'pm25_concentration', 'improvement_percent')
    list_filter = ('scenario__status', 'timestamp')
    search_fields = ('scenario__name', 'scenario__user__username')
    ordering = ('-timestamp',)


@admin.register(ScenarioComparison)
class ScenarioComparisonAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'user__username')
    filter_horizontal = ('scenarios',)
    ordering = ('-created_at',)


@admin.register(ImpactFactor)
class ImpactFactorAdmin(admin.ModelAdmin):
    list_display = ('name', 'factor_type', 'pm25_coefficient', 'no2_coefficient', 'is_active', 'created_at')
    list_filter = ('factor_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)