from django.urls import path
from . import views

app_name = 'eco_action'

urlpatterns = [
    path('', views.eco_dashboard, name='dashboard'),
    path('policies/', views.policy_list, name='policies'),
    path('policies/<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('policies/<int:policy_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('community-actions/', views.community_actions, name='community_actions'),
    path('community-actions/<int:action_id>/', views.action_detail, name='action_detail'),
    path('community-actions/<int:action_id>/join/', views.join_action, name='join_action'),
    path('community-actions/<int:action_id>/leave/', views.leave_action, name='leave_action'),
    path('community-actions/create/', views.create_action, name='create_action'),
    path('tips/', views.eco_tips, name='tips'),
    path('tips/<int:tip_id>/', views.tip_detail, name='tip_detail'),
    path('tips/<int:tip_id>/like/', views.like_tip, name='like_tip'),
    path('profile/', views.user_eco_profile, name='profile'),
    path('profile/edit/', views.edit_eco_profile, name='edit_profile'),
]