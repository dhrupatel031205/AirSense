from django.urls import path
from . import views

app_name = 'social_impact'

urlpatterns = [
    path('', views.social_dashboard, name='dashboard'),
    
    # Posts
    path('posts/', views.post_feed, name='feed'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    
    # Air Quality Reports
    path('reports/', views.air_quality_reports, name='reports'),
    path('reports/create/', views.create_report, name='create_report'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    
    # Community Groups
    path('groups/', views.community_groups, name='groups'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/post/', views.create_group_post, name='create_group_post'),
    
    # Environmental Challenges
    path('challenges/', views.environmental_challenges, name='challenges'),
    path('challenges/create/', views.create_challenge, name='create_challenge'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    path('challenges/<int:challenge_id>/update-progress/', views.update_challenge_progress, name='update_progress'),
    
    # User Profiles
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_social_profile, name='edit_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    
    # Leaderboards
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('achievements/', views.achievements, name='achievements'),
]