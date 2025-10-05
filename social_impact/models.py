from django.db import models
from django.contrib.auth.models import User
from dashboard.models import AirQualityReading


class SocialPost(models.Model):
    """Social posts about air quality and environmental issues"""
    POST_TYPES = [
        ('observation', 'Air Quality Observation'),
        ('concern', 'Environmental Concern'),
        ('news', 'News/Article Share'),
        ('question', 'Question'),
        ('tip', 'Environmental Tip'),
        ('achievement', 'Personal Achievement'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=20, choices=POST_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Associated air quality data
    aqi_reading = models.ForeignKey(AirQualityReading, on_delete=models.SET_NULL, null=True, blank=True)
    reported_aqi = models.IntegerField(null=True, blank=True)
    
    # Media
    image = models.ImageField(upload_to='social_posts/', blank=True)
    
    # Engagement
    likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
    is_verified = models.BooleanField(default=False)  # For official/verified posts
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.author.username}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    """Comments on social posts"""
    post = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # For replies
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    @property
    def is_reply(self):
        return self.parent is not None


class CommunityGroup(models.Model):
    """Community groups focused on environmental issues"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    
    # Group settings
    is_public = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    
    # Management
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    moderators = models.ManyToManyField(User, blank=True, related_name='moderated_groups')
    members = models.ManyToManyField(User, blank=True, related_name='joined_groups')
    
    # Metadata
    image = models.ImageField(upload_to='community_groups/', blank=True)
    website_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()


class GroupPost(models.Model):
    """Posts within community groups"""
    group = models.ForeignKey(CommunityGroup, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Media
    image = models.ImageField(upload_to='group_posts/', blank=True)
    
    # Engagement
    likes = models.ManyToManyField(User, blank=True, related_name='liked_group_posts')
    
    # Moderation
    is_pinned = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.group.name}"


class AirQualityReport(models.Model):
    """User-submitted air quality reports"""
    VISIBILITY_CHOICES = [
        ('excellent', 'Excellent (>40km)'),
        ('good', 'Good (20-40km)'),
        ('fair', 'Fair (10-20km)'),
        ('poor', 'Poor (5-10km)'),
        ('very_poor', 'Very Poor (<5km)'),
    ]

    WEATHER_CONDITIONS = [
        ('clear', 'Clear'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('windy', 'Windy'),
        ('foggy', 'Foggy'),
        ('smoky', 'Smoky'),
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Observations
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES)
    weather_condition = models.CharField(max_length=20, choices=WEATHER_CONDITIONS)
    smell_noticed = models.BooleanField(default=False)
    smell_description = models.CharField(max_length=200, blank=True)
    symptoms_experienced = models.BooleanField(default=False)
    symptom_description = models.CharField(max_length=200, blank=True)
    
    # Estimated AQI (user's perception)
    estimated_aqi = models.IntegerField()
    confidence_level = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low Confidence'),
            ('medium', 'Medium Confidence'),
            ('high', 'High Confidence'),
        ],
        default='medium'
    )
    
    # Media
    photo = models.ImageField(upload_to='air_quality_reports/', blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_reports')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter.username} - {self.location} (AQI: {self.estimated_aqi})"


class EnvironmentalChallenge(models.Model):
    """Environmental challenges for community engagement"""
    CHALLENGE_TYPES = [
        ('reduction', 'Pollution Reduction'),
        ('awareness', 'Awareness Building'),
        ('action', 'Environmental Action'),
        ('education', 'Education/Learning'),
        ('monitoring', 'Air Quality Monitoring'),
    ]

    DIFFICULTY_LEVELS = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS)
    
    # Challenge details
    duration_days = models.PositiveIntegerField()
    points_reward = models.PositiveIntegerField(default=10)
    requirements = models.TextField()  # What users need to do
    
    # Timing
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Management
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, blank=True, related_name='joined_challenges')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    @property
    def participant_count(self):
        return self.participants.count()


class ChallengeParticipation(models.Model):
    """User participation in environmental challenges"""
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(EnvironmentalChallenge, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined')
    
    # Progress tracking
    progress_notes = models.TextField(blank=True)
    evidence_photo = models.ImageField(upload_to='challenge_evidence/', blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    # Points and rewards
    points_earned = models.PositiveIntegerField(default=0)
    
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'challenge']

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.status})"


class UserSocialProfile(models.Model):
    """Extended social profile for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Social stats
    posts_count = models.PositiveIntegerField(default=0)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    
    # Environmental engagement
    total_points = models.PositiveIntegerField(default=0)
    challenges_completed = models.PositiveIntegerField(default=0)
    reports_submitted = models.PositiveIntegerField(default=0)
    
    # Privacy settings
    is_profile_public = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_stats = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Social Profile"


class Follow(models.Model):
    """User following relationships"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['follower', 'following']

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"