from django.contrib import admin
from .models import (SocialPost, Comment, CommunityGroup, GroupPost, AirQualityReport, 
                     EnvironmentalChallenge, ChallengeParticipation, UserSocialProfile, Follow)


@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'post_type', 'location', 'like_count', 'is_verified', 'created_at')
    list_filter = ('post_type', 'is_verified', 'is_pinned', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'location')
    filter_horizontal = ('likes',)
    ordering = ('-created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_reply', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username', 'post__title')
    ordering = ('-created_at',)


@admin.register(CommunityGroup)
class CommunityGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'member_count', 'is_public', 'creator', 'created_at')
    list_filter = ('is_public', 'requires_approval', 'created_at')
    search_fields = ('name', 'description', 'location')
    filter_horizontal = ('moderators', 'members')
    ordering = ('name',)


@admin.register(GroupPost)
class GroupPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'group', 'is_pinned', 'is_approved', 'created_at')
    list_filter = ('is_pinned', 'is_approved', 'created_at', 'group')
    search_fields = ('title', 'content', 'author__username')
    filter_horizontal = ('likes',)
    ordering = ('-created_at',)


@admin.register(AirQualityReport)
class AirQualityReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'location', 'estimated_aqi', 'visibility', 'is_verified', 'created_at')
    list_filter = ('visibility', 'weather_condition', 'is_verified', 'confidence_level', 'created_at')
    search_fields = ('reporter__username', 'location', 'notes')
    ordering = ('-created_at',)


@admin.register(EnvironmentalChallenge)
class EnvironmentalChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'difficulty', 'participant_count', 'start_date', 'is_active')
    list_filter = ('challenge_type', 'difficulty', 'is_active', 'is_featured', 'start_date')
    search_fields = ('title', 'description', 'creator__username')
    filter_horizontal = ('participants',)
    ordering = ('-start_date',)


@admin.register(ChallengeParticipation)
class ChallengeParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'status', 'points_earned', 'completion_date')
    list_filter = ('status', 'joined_at', 'completion_date')
    search_fields = ('user__username', 'challenge__title')
    ordering = ('-joined_at',)


@admin.register(UserSocialProfile)
class UserSocialProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'total_points', 'challenges_completed', 'is_profile_public')
    list_filter = ('is_profile_public', 'show_location', 'show_stats', 'created_at')
    search_fields = ('user__username', 'bio', 'location')
    ordering = ('-total_points',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    ordering = ('-created_at',)