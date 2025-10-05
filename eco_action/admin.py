from django.contrib import admin
from .models import PolicyCategory, EnvironmentalPolicy, CommunityAction, EcoTip, UserEcoProfile, PolicyFeedback


@admin.register(PolicyCategory)
class PolicyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(EnvironmentalPolicy)
class EnvironmentalPolicyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'policy_type', 'impact_level', 'is_active', 'created_at')
    list_filter = ('policy_type', 'impact_level', 'is_active', 'category', 'created_at')
    search_fields = ('title', 'description', 'location')
    ordering = ('-created_at',)


@admin.register(CommunityAction)
class CommunityActionAdmin(admin.ModelAdmin):
    list_display = ('title', 'action_type', 'organizer', 'status', 'participant_count', 'start_date')
    list_filter = ('action_type', 'status', 'start_date', 'created_at')
    search_fields = ('title', 'description', 'location', 'organizer__username')
    filter_horizontal = ('participants',)
    ordering = ('-start_date',)


@admin.register(EcoTip)
class EcoTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty_level', 'is_featured', 'like_count', 'created_at')
    list_filter = ('category', 'difficulty_level', 'is_featured', 'created_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('likes',)
    ordering = ('-created_at',)


@admin.register(UserEcoProfile)
class UserEcoProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'actions_participated', 'actions_organized', 'notification_frequency', 'is_public_profile')
    list_filter = ('notification_frequency', 'is_public_profile', 'created_at')
    search_fields = ('user__username', 'user__email')
    filter_horizontal = ('preferred_categories',)


@admin.register(PolicyFeedback)
class PolicyFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'policy', 'feedback_type', 'is_anonymous', 'created_at')
    list_filter = ('feedback_type', 'is_anonymous', 'created_at')
    search_fields = ('user__username', 'policy__title', 'comment')
    ordering = ('-created_at',)