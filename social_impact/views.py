from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from .models import (
    SocialPost, Comment, CommunityGroup, GroupPost, AirQualityReport,
    EnvironmentalChallenge, ChallengeParticipation, UserSocialProfile, Follow
)


def social_dashboard(request):
    """Main social impact dashboard"""
    # Recent posts
    recent_posts = SocialPost.objects.filter(
        is_verified=True
    ).select_related('author')[:5]
    
    # Active challenges
    active_challenges = EnvironmentalChallenge.objects.filter(
        is_active=True,
        end_date__gte=timezone.now().date()
    ).annotate(
        participant_count=Count('participants')
    )[:3]
    
    # Popular groups
    popular_groups = CommunityGroup.objects.filter(
        is_public=True
    ).annotate(
        member_count=Count('members')
    ).order_by('-member_count')[:5]
    
    # Recent reports
    recent_reports = AirQualityReport.objects.filter(
        is_verified=True
    ).select_related('reporter')[:5]
    
    # User-specific data if logged in
    user_stats = None
    if request.user.is_authenticated:
        try:
            user_profile = UserSocialProfile.objects.get(user=request.user)
            user_stats = {
                'total_points': user_profile.total_points,
                'posts_count': user_profile.posts_count,
                'challenges_completed': user_profile.challenges_completed,
            }
        except UserSocialProfile.DoesNotExist:
            user_stats = {'total_points': 0, 'posts_count': 0, 'challenges_completed': 0}
    
    context = {
        'title': 'Social Impact Dashboard',
        'recent_posts': recent_posts,
        'active_challenges': active_challenges,
        'popular_groups': popular_groups,
        'recent_reports': recent_reports,
        'user_stats': user_stats,
    }
    return render(request, 'social_impact/dashboard.html', context)


def post_feed(request):
    """Social media feed of posts"""
    posts = SocialPost.objects.all().select_related('author').prefetch_related('likes')
    
    # Filter by post type
    post_type = request.GET.get('type')
    if post_type:
        posts = posts.filter(post_type=post_type)
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        posts = posts.filter(location__icontains=location_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    # Pagination (simplified)
    posts = posts[:20]
    
    context = {
        'title': 'Community Feed',
        'posts': posts,
        'post_type': post_type,
        'location_filter': location_filter,
        'search_query': search_query,
        'post_types': SocialPost.POST_TYPES,
    }
    return render(request, 'social_impact/feed.html', context)


@login_required
def create_post(request):
    """Create a new social post"""
    if request.method == 'POST':
        post = SocialPost(
            author=request.user,
            post_type=request.POST.get('post_type'),
            title=request.POST.get('title'),
            content=request.POST.get('content'),
            location=request.POST.get('location'),
        )
        
        # Handle coordinates if provided
        if request.POST.get('latitude') and request.POST.get('longitude'):
            post.latitude = float(request.POST.get('latitude'))
            post.longitude = float(request.POST.get('longitude'))
        
        # Handle reported AQI
        if request.POST.get('reported_aqi'):
            post.reported_aqi = int(request.POST.get('reported_aqi'))
        
        # Handle image upload
        if request.FILES.get('image'):
            post.image = request.FILES['image']
        
        post.save()
        
        # Update user profile stats
        profile, created = UserSocialProfile.objects.get_or_create(user=request.user)
        profile.posts_count += 1
        profile.save()
        
        messages.success(request, 'Post created successfully!')
        return redirect('social_impact:post_detail', post_id=post.id)
    
    context = {
        'title': 'Create Post',
        'post_types': SocialPost.POST_TYPES,
    }
    return render(request, 'social_impact/create_post.html', context)


def post_detail(request, post_id):
    """Post detail view with comments"""
    post = get_object_or_404(SocialPost, id=post_id)
    comments = post.comments.filter(parent__isnull=True).order_by('created_at')
    
    # Check if user has liked the post
    user_liked = False
    if request.user.is_authenticated:
        user_liked = post.likes.filter(id=request.user.id).exists()
    
    context = {
        'title': post.title,
        'post': post,
        'comments': comments,
        'user_liked': user_liked,
    }
    return render(request, 'social_impact/post_detail.html', context)


@login_required
def like_post(request, post_id):
    """Like/unlike a post"""
    post = get_object_or_404(SocialPost, id=post_id)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({
            'liked': liked,
            'like_count': post.like_count
        })
    
    return redirect('social_impact:post_detail', post_id=post.id)


@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    post = get_object_or_404(SocialPost, id=post_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        comment = Comment(
            post=post,
            author=request.user,
            content=content
        )
        
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, post=post)
                comment.parent = parent_comment
            except Comment.DoesNotExist:
                pass
        
        comment.save()
        messages.success(request, 'Comment added!')
    
    return redirect('social_impact:post_detail', post_id=post.id)


def air_quality_reports(request):
    """List of user-submitted air quality reports"""
    reports = AirQualityReport.objects.all().select_related('reporter')
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        reports = reports.filter(location__icontains=location_filter)
    
    # Filter by verification status
    verified_filter = request.GET.get('verified')
    if verified_filter == 'true':
        reports = reports.filter(is_verified=True)
    elif verified_filter == 'false':
        reports = reports.filter(is_verified=False)
    
    context = {
        'title': 'Air Quality Reports',
        'reports': reports,
        'location_filter': location_filter,
        'verified_filter': verified_filter,
    }
    return render(request, 'social_impact/reports.html', context)


@login_required
def create_report(request):
    """Create a new air quality report"""
    if request.method == 'POST':
        report = AirQualityReport(
            reporter=request.user,
            location=request.POST.get('location'),
            latitude=float(request.POST.get('latitude', 0)),
            longitude=float(request.POST.get('longitude', 0)),
            visibility=request.POST.get('visibility'),
            weather_condition=request.POST.get('weather_condition'),
            smell_noticed='smell_noticed' in request.POST,
            smell_description=request.POST.get('smell_description', ''),
            symptoms_experienced='symptoms_experienced' in request.POST,
            symptom_description=request.POST.get('symptom_description', ''),
            estimated_aqi=int(request.POST.get('estimated_aqi')),
            confidence_level=request.POST.get('confidence_level'),
            notes=request.POST.get('notes', ''),
        )
        
        # Handle photo upload
        if request.FILES.get('photo'):
            report.photo = request.FILES['photo']
        
        report.save()
        
        # Update user profile stats
        profile, created = UserSocialProfile.objects.get_or_create(user=request.user)
        profile.reports_submitted += 1
        profile.save()
        
        messages.success(request, 'Air quality report submitted successfully!')
        return redirect('social_impact:report_detail', report_id=report.id)
    
    context = {
        'title': 'Submit Air Quality Report',
        'visibility_choices': AirQualityReport.VISIBILITY_CHOICES,
        'weather_conditions': AirQualityReport.WEATHER_CONDITIONS,
    }
    return render(request, 'social_impact/create_report.html', context)


def report_detail(request, report_id):
    """Air quality report detail view"""
    report = get_object_or_404(AirQualityReport, id=report_id)
    
    context = {
        'title': f'Report: {report.location}',
        'report': report,
    }
    return render(request, 'social_impact/report_detail.html', context)


def community_groups(request):
    """List of community groups"""
    groups = CommunityGroup.objects.filter(is_public=True).annotate(
        member_count=Count('members')
    )
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter:
        groups = groups.filter(location__icontains=location_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'title': 'Community Groups',
        'groups': groups,
        'location_filter': location_filter,
        'search_query': search_query,
    }
    return render(request, 'social_impact/groups.html', context)


@login_required
def create_group(request):
    """Create a new community group"""
    if request.method == 'POST':
        group = CommunityGroup(
            creator=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            location=request.POST.get('location'),
            is_public='is_public' in request.POST,
            requires_approval='requires_approval' in request.POST,
            website_url=request.POST.get('website_url', ''),
            contact_email=request.POST.get('contact_email', ''),
        )
        
        # Handle image upload
        if request.FILES.get('image'):
            group.image = request.FILES['image']
        
        group.save()
        
        # Add creator as a member and moderator
        group.members.add(request.user)
        group.moderators.add(request.user)
        
        messages.success(request, f'Community group "{group.name}" created successfully!')
        return redirect('social_impact:group_detail', group_id=group.id)
    
    context = {
        'title': 'Create Community Group',
    }
    return render(request, 'social_impact/create_group.html', context)


def group_detail(request, group_id):
    """Community group detail view"""
    group = get_object_or_404(CommunityGroup, id=group_id)
    
    if not group.is_public and not group.members.filter(id=request.user.id).exists():
        messages.error(request, 'This group is private.')
        return redirect('social_impact:groups')
    
    # Get group posts
    posts = group.posts.filter(is_approved=True).select_related('author')[:10]
    
    # Check if user is a member
    is_member = False
    is_moderator = False
    if request.user.is_authenticated:
        is_member = group.members.filter(id=request.user.id).exists()
        is_moderator = group.moderators.filter(id=request.user.id).exists()
    
    context = {
        'title': group.name,
        'group': group,
        'posts': posts,
        'is_member': is_member,
        'is_moderator': is_moderator,
    }
    return render(request, 'social_impact/group_detail.html', context)


@login_required
def join_group(request, group_id):
    """Join a community group"""
    group = get_object_or_404(CommunityGroup, id=group_id)
    
    if group.members.filter(id=request.user.id).exists():
        messages.info(request, 'You are already a member of this group.')
    else:
        group.members.add(request.user)
        messages.success(request, f'You have joined "{group.name}"!')
    
    return redirect('social_impact:group_detail', group_id=group.id)


@login_required
def leave_group(request, group_id):
    """Leave a community group"""
    group = get_object_or_404(CommunityGroup, id=group_id)
    
    if group.members.filter(id=request.user.id).exists():
        group.members.remove(request.user)
        if group.moderators.filter(id=request.user.id).exists():
            group.moderators.remove(request.user)
        messages.success(request, f'You have left "{group.name}".')
    else:
        messages.info(request, 'You are not a member of this group.')
    
    return redirect('social_impact:group_detail', group_id=group.id)


@login_required
def create_group_post(request, group_id):
    """Create a post in a community group"""
    group = get_object_or_404(CommunityGroup, id=group_id)
    
    if not group.members.filter(id=request.user.id).exists():
        messages.error(request, 'You must be a member to post in this group.')
        return redirect('social_impact:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        post = GroupPost(
            group=group,
            author=request.user,
            title=request.POST.get('title'),
            content=request.POST.get('content'),
        )
        
        # Handle image upload
        if request.FILES.get('image'):
            post.image = request.FILES['image']
        
        # Auto-approve for moderators
        if group.moderators.filter(id=request.user.id).exists():
            post.is_approved = True
        
        post.save()
        messages.success(request, 'Post created successfully!')
        return redirect('social_impact:group_detail', group_id=group.id)
    
    context = {
        'title': f'Create Post in {group.name}',
        'group': group,
    }
    return render(request, 'social_impact/create_group_post.html', context)


def environmental_challenges(request):
    """List of environmental challenges"""
    challenges = EnvironmentalChallenge.objects.filter(
        is_active=True
    ).annotate(
        participant_count=Count('participants')
    ).order_by('-is_featured', '-start_date')
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        challenges = challenges.filter(challenge_type=type_filter)
    
    # Filter by difficulty
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        challenges = challenges.filter(difficulty=difficulty_filter)
    
    context = {
        'title': 'Environmental Challenges',
        'challenges': challenges,
        'type_filter': type_filter,
        'difficulty_filter': difficulty_filter,
        'challenge_types': EnvironmentalChallenge.CHALLENGE_TYPES,
    }
    return render(request, 'social_impact/challenges.html', context)


@login_required
def create_challenge(request):
    """Create a new environmental challenge"""
    if request.method == 'POST':
        challenge = EnvironmentalChallenge(
            creator=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            challenge_type=request.POST.get('challenge_type'),
            difficulty=request.POST.get('difficulty'),
            duration_days=int(request.POST.get('duration_days')),
            points_reward=int(request.POST.get('points_reward')),
            requirements=request.POST.get('requirements'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
        )
        
        challenge.save()
        messages.success(request, f'Challenge "{challenge.title}" created successfully!')
        return redirect('social_impact:challenge_detail', challenge_id=challenge.id)
    
    context = {
        'title': 'Create Environmental Challenge',
        'challenge_types': EnvironmentalChallenge.CHALLENGE_TYPES,
    }
    return render(request, 'social_impact/create_challenge.html', context)


def challenge_detail(request, challenge_id):
    """Environmental challenge detail view"""
    challenge = get_object_or_404(EnvironmentalChallenge, id=challenge_id)
    
    # Check if user has joined
    user_participation = None
    if request.user.is_authenticated:
        try:
            user_participation = ChallengeParticipation.objects.get(
                user=request.user,
                challenge=challenge
            )
        except ChallengeParticipation.DoesNotExist:
            pass
    
    context = {
        'title': challenge.title,
        'challenge': challenge,
        'user_participation': user_participation,
    }
    return render(request, 'social_impact/challenge_detail.html', context)


@login_required
def join_challenge(request, challenge_id):
    """Join an environmental challenge"""
    challenge = get_object_or_404(EnvironmentalChallenge, id=challenge_id)
    
    participation, created = ChallengeParticipation.objects.get_or_create(
        user=request.user,
        challenge=challenge
    )
    
    if created:
        messages.success(request, f'You have joined the challenge "{challenge.title}"!')
    else:
        messages.info(request, 'You have already joined this challenge.')
    
    return redirect('social_impact:challenge_detail', challenge_id=challenge.id)


@login_required
def update_challenge_progress(request, challenge_id):
    """Update progress on a challenge"""
    challenge = get_object_or_404(EnvironmentalChallenge, id=challenge_id)
    
    try:
        participation = ChallengeParticipation.objects.get(
            user=request.user,
            challenge=challenge
        )
    except ChallengeParticipation.DoesNotExist:
        messages.error(request, 'You have not joined this challenge.')
        return redirect('social_impact:challenge_detail', challenge_id=challenge.id)
    
    if request.method == 'POST':
        participation.progress_notes = request.POST.get('progress_notes')
        participation.status = request.POST.get('status')
        
        # Handle evidence photo
        if request.FILES.get('evidence_photo'):
            participation.evidence_photo = request.FILES['evidence_photo']
        
        # Award points if completed
        if request.POST.get('status') == 'completed' and participation.status != 'completed':
            participation.completion_date = timezone.now()
            participation.points_earned = challenge.points_reward
            
            # Update user profile
            profile, created = UserSocialProfile.objects.get_or_create(user=request.user)
            profile.total_points += challenge.points_reward
            profile.challenges_completed += 1
            profile.save()
        
        participation.save()
        messages.success(request, 'Challenge progress updated!')
    
    return redirect('social_impact:challenge_detail', challenge_id=challenge.id)


def user_profile(request, username):
    """User profile view"""
    profile_user = get_object_or_404(User, username=username)
    
    try:
        social_profile = UserSocialProfile.objects.get(user=profile_user)
    except UserSocialProfile.DoesNotExist:
        social_profile = UserSocialProfile.objects.create(user=profile_user)
    
    # Check if current user follows this user
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user
        ).exists()
    
    # Get user's recent posts
    recent_posts = SocialPost.objects.filter(author=profile_user)[:5]
    
    context = {
        'title': f"{profile_user.get_full_name() or profile_user.username}'s Profile",
        'profile_user': profile_user,
        'social_profile': social_profile,
        'is_following': is_following,
        'recent_posts': recent_posts,
    }
    return render(request, 'social_impact/user_profile.html', context)


@login_required
def edit_social_profile(request):
    """Edit user's social profile"""
    try:
        social_profile = UserSocialProfile.objects.get(user=request.user)
    except UserSocialProfile.DoesNotExist:
        social_profile = UserSocialProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        social_profile.bio = request.POST.get('bio', '')
        social_profile.location = request.POST.get('location', '')
        social_profile.is_profile_public = 'is_profile_public' in request.POST
        social_profile.show_location = 'show_location' in request.POST
        social_profile.show_stats = 'show_stats' in request.POST
        social_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('social_impact:user_profile', username=request.user.username)
    
    context = {
        'title': 'Edit Profile',
        'social_profile': social_profile,
    }
    return render(request, 'social_impact/edit_profile.html', context)


@login_required
def follow_user(request, username):
    """Follow a user"""
    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        messages.error(request, 'You cannot follow yourself.')
    else:
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        
        if created:
            messages.success(request, f'You are now following {target_user.username}!')
        else:
            messages.info(request, f'You are already following {target_user.username}.')
    
    return redirect('social_impact:user_profile', username=username)


@login_required
def unfollow_user(request, username):
    """Unfollow a user"""
    target_user = get_object_or_404(User, username=username)
    
    try:
        follow = Follow.objects.get(follower=request.user, following=target_user)
        follow.delete()
        messages.success(request, f'You have unfollowed {target_user.username}.')
    except Follow.DoesNotExist:
        messages.info(request, f'You are not following {target_user.username}.')
    
    return redirect('social_impact:user_profile', username=username)


def leaderboard(request):
    """Leaderboard of top users"""
    top_users = UserSocialProfile.objects.filter(
        is_profile_public=True,
        show_stats=True
    ).select_related('user').order_by('-total_points')[:50]
    
    context = {
        'title': 'Leaderboard',
        'top_users': top_users,
    }
    return render(request, 'social_impact/leaderboard.html', context)


@login_required
def achievements(request):
    """User's achievements and statistics"""
    try:
        social_profile = UserSocialProfile.objects.get(user=request.user)
    except UserSocialProfile.DoesNotExist:
        social_profile = UserSocialProfile.objects.create(user=request.user)
    
    # Get user's challenge participations
    participations = ChallengeParticipation.objects.filter(
        user=request.user
    ).select_related('challenge')
    
    context = {
        'title': 'My Achievements',
        'social_profile': social_profile,
        'participations': participations,
    }
    return render(request, 'social_impact/achievements.html', context)