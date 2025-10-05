from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from .models import (
    EnvironmentalPolicy, CommunityAction, EcoTip, 
    UserEcoProfile, PolicyFeedback, PolicyCategory
)


def eco_dashboard(request):
    """Main eco action dashboard"""
    # Get featured content
    featured_policies = EnvironmentalPolicy.objects.filter(
        is_active=True,
        impact_level='high'
    )[:3]
    
    upcoming_actions = CommunityAction.objects.filter(
        status='active',
        start_date__gte=timezone.now()
    ).order_by('start_date')[:3]
    
    featured_tips = EcoTip.objects.filter(is_featured=True)[:3]
    
    # User-specific data if logged in
    user_actions = None
    user_profile = None
    if request.user.is_authenticated:
        user_actions = CommunityAction.objects.filter(
            participants=request.user
        )[:3]
        try:
            user_profile = UserEcoProfile.objects.get(user=request.user)
        except UserEcoProfile.DoesNotExist:
            user_profile = None
    
    context = {
        'title': 'Eco Action Dashboard',
        'featured_policies': featured_policies,
        'upcoming_actions': upcoming_actions,
        'featured_tips': featured_tips,
        'user_actions': user_actions,
        'user_profile': user_profile,
    }
    return render(request, 'eco_action/dashboard.html', context)


def policy_list(request):
    """List of environmental policies"""
    policies = EnvironmentalPolicy.objects.filter(is_active=True)
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        policies = policies.filter(category__id=category_filter)
    
    # Filter by policy type
    type_filter = request.GET.get('type')
    if type_filter:
        policies = policies.filter(policy_type=type_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        policies = policies.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get categories for filter dropdown
    categories = PolicyCategory.objects.all()
    
    context = {
        'title': 'Environmental Policies',
        'policies': policies,
        'categories': categories,
        'selected_category': category_filter,
        'selected_type': type_filter,
        'search_query': search_query,
    }
    return render(request, 'eco_action/policy_list.html', context)


def policy_detail(request, policy_id):
    """Policy detail view"""
    policy = get_object_or_404(EnvironmentalPolicy, id=policy_id)
    
    # Get user feedback if logged in
    user_feedback = None
    if request.user.is_authenticated:
        try:
            user_feedback = PolicyFeedback.objects.get(
                user=request.user,
                policy=policy
            )
        except PolicyFeedback.DoesNotExist:
            pass
    
    # Get feedback statistics
    feedback_stats = PolicyFeedback.objects.filter(policy=policy).values(
        'feedback_type'
    ).annotate(count=Count('id'))
    
    context = {
        'title': policy.title,
        'policy': policy,
        'user_feedback': user_feedback,
        'feedback_stats': feedback_stats,
    }
    return render(request, 'eco_action/policy_detail.html', context)


@login_required
def submit_feedback(request, policy_id):
    """Submit feedback on a policy"""
    policy = get_object_or_404(EnvironmentalPolicy, id=policy_id)
    
    if request.method == 'POST':
        feedback_type = request.POST.get('feedback_type')
        comment = request.POST.get('comment', '')
        is_anonymous = 'is_anonymous' in request.POST
        
        # Update or create feedback
        feedback, created = PolicyFeedback.objects.update_or_create(
            user=request.user,
            policy=policy,
            defaults={
                'feedback_type': feedback_type,
                'comment': comment,
                'is_anonymous': is_anonymous,
            }
        )
        
        action = 'submitted' if created else 'updated'
        messages.success(request, f'Your feedback has been {action}!')
        
        return redirect('eco_action:policy_detail', policy_id=policy.id)
    
    return redirect('eco_action:policy_detail', policy_id=policy.id)


def community_actions(request):
    """List of community actions"""
    actions = CommunityAction.objects.all()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        actions = actions.filter(status=status_filter)
    else:
        # Default to active and planning actions
        actions = actions.filter(status__in=['planning', 'active'])
    
    # Filter by action type
    type_filter = request.GET.get('type')
    if type_filter:
        actions = actions.filter(action_type=type_filter)
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        actions = actions.filter(location__icontains=location_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        actions = actions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {
        'title': 'Community Actions',
        'actions': actions,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'location_filter': location_filter,
        'search_query': search_query,
    }
    return render(request, 'eco_action/community_actions.html', context)


def action_detail(request, action_id):
    """Community action detail view"""
    action = get_object_or_404(CommunityAction, id=action_id)
    
    # Check if user has joined
    user_joined = False
    if request.user.is_authenticated:
        user_joined = action.participants.filter(id=request.user.id).exists()
    
    context = {
        'title': action.title,
        'action': action,
        'user_joined': user_joined,
    }
    return render(request, 'eco_action/action_detail.html', context)


@login_required
def join_action(request, action_id):
    """Join a community action"""
    action = get_object_or_404(CommunityAction, id=action_id)
    
    if action.is_full:
        messages.error(request, 'This action is already full!')
    elif action.participants.filter(id=request.user.id).exists():
        messages.info(request, 'You have already joined this action!')
    else:
        action.participants.add(request.user)
        messages.success(request, f'You have successfully joined "{action.title}"!')
        
        # Update user eco profile
        profile, created = UserEcoProfile.objects.get_or_create(user=request.user)
        profile.actions_participated += 1
        profile.save()
    
    return redirect('eco_action:action_detail', action_id=action.id)


@login_required
def leave_action(request, action_id):
    """Leave a community action"""
    action = get_object_or_404(CommunityAction, id=action_id)
    
    if action.participants.filter(id=request.user.id).exists():
        action.participants.remove(request.user)
        messages.success(request, f'You have left "{action.title}".')
    else:
        messages.info(request, 'You are not part of this action.')
    
    return redirect('eco_action:action_detail', action_id=action.id)


@login_required
def create_action(request):
    """Create a new community action"""
    if request.method == 'POST':
        # Handle form submission
        # This is a simplified version - you'd want to use Django forms
        title = request.POST.get('title')
        description = request.POST.get('description')
        action_type = request.POST.get('action_type')
        location = request.POST.get('location')
        start_date = request.POST.get('start_date')
        
        action = CommunityAction.objects.create(
            title=title,
            description=description,
            action_type=action_type,
            location=location,
            start_date=start_date,
            organizer=request.user
        )
        
        # Update user eco profile
        profile, created = UserEcoProfile.objects.get_or_create(user=request.user)
        profile.actions_organized += 1
        profile.save()
        
        messages.success(request, 'Community action created successfully!')
        return redirect('eco_action:action_detail', action_id=action.id)
    
    context = {
        'title': 'Create Community Action',
        'action_types': CommunityAction.ACTION_TYPES,
    }
    return render(request, 'eco_action/create_action.html', context)


def eco_tips(request):
    """List of eco tips"""
    tips = EcoTip.objects.all()
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        tips = tips.filter(category=category_filter)
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        tips = tips.filter(difficulty_level=difficulty_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        tips = tips.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    context = {
        'title': 'Eco Tips',
        'tips': tips,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'search_query': search_query,
        'categories': EcoTip.TIP_CATEGORIES,
    }
    return render(request, 'eco_action/tips.html', context)


def tip_detail(request, tip_id):
    """Eco tip detail view"""
    tip = get_object_or_404(EcoTip, id=tip_id)
    
    # Check if user has liked the tip
    user_liked = False
    if request.user.is_authenticated:
        user_liked = tip.likes.filter(id=request.user.id).exists()
    
    context = {
        'title': tip.title,
        'tip': tip,
        'user_liked': user_liked,
    }
    return render(request, 'eco_action/tip_detail.html', context)


@login_required
def like_tip(request, tip_id):
    """Like/unlike an eco tip"""
    tip = get_object_or_404(EcoTip, id=tip_id)
    
    if tip.likes.filter(id=request.user.id).exists():
        tip.likes.remove(request.user)
        liked = False
    else:
        tip.likes.add(request.user)
        liked = True
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'liked': liked,
            'like_count': tip.like_count
        })
    
    return redirect('eco_action:tip_detail', tip_id=tip.id)


@login_required
def user_eco_profile(request):
    """User's eco profile"""
    profile, created = UserEcoProfile.objects.get_or_create(user=request.user)
    
    # Get user's actions
    organized_actions = CommunityAction.objects.filter(organizer=request.user)
    participated_actions = CommunityAction.objects.filter(participants=request.user)
    
    # Get user's feedback
    policy_feedback = PolicyFeedback.objects.filter(user=request.user)
    
    context = {
        'title': 'My Eco Profile',
        'profile': profile,
        'organized_actions': organized_actions,
        'participated_actions': participated_actions,
        'policy_feedback': policy_feedback,
    }
    return render(request, 'eco_action/profile.html', context)


@login_required
def edit_eco_profile(request):
    """Edit user's eco profile"""
    profile, created = UserEcoProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.carbon_footprint_goal = float(request.POST.get('carbon_footprint_goal', 0))
        profile.notification_frequency = request.POST.get('notification_frequency', 'weekly')
        profile.is_public_profile = 'is_public_profile' in request.POST
        
        # Update preferred categories
        selected_categories = request.POST.getlist('preferred_categories')
        profile.preferred_categories.clear()
        for category_id in selected_categories:
            try:
                category = PolicyCategory.objects.get(id=category_id)
                profile.preferred_categories.add(category)
            except PolicyCategory.DoesNotExist:
                pass
        
        profile.save()
        messages.success(request, 'Eco profile updated successfully!')
        return redirect('eco_action:profile')
    
    categories = PolicyCategory.objects.all()
    
    context = {
        'title': 'Edit Eco Profile',
        'profile': profile,
        'categories': categories,
    }
    return render(request, 'eco_action/edit_profile.html', context)