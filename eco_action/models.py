from django.db import models
from django.contrib.auth.models import User


class PolicyCategory(models.Model):
    """Categories for environmental policies"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class/name
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Policy Categories'

    def __str__(self):
        return self.name


class EnvironmentalPolicy(models.Model):
    """Environmental policies and recommendations"""
    POLICY_TYPES = [
        ('local', 'Local Policy'),
        ('regional', 'Regional Policy'),
        ('national', 'National Policy'),
        ('international', 'International Policy'),
        ('recommendation', 'Recommendation'),
    ]

    IMPACT_LEVELS = [
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact'),
        ('critical', 'Critical Impact'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(PolicyCategory, on_delete=models.CASCADE)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    impact_level = models.CharField(max_length=10, choices=IMPACT_LEVELS)
    location = models.CharField(max_length=100, blank=True)  # Applicable location
    source_url = models.URLField(blank=True)
    implementation_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CommunityAction(models.Model):
    """Community environmental actions and initiatives"""
    ACTION_TYPES = [
        ('cleanup', 'Environmental Cleanup'),
        ('tree_planting', 'Tree Planting'),
        ('awareness', 'Awareness Campaign'),
        ('monitoring', 'Air Quality Monitoring'),
        ('advocacy', 'Policy Advocacy'),
        ('education', 'Environmental Education'),
    ]

    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    location = models.CharField(max_length=100)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_actions')
    participants = models.ManyToManyField(User, blank=True, related_name='joined_actions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=50)
    registration_required = models.BooleanField(default=False)
    contact_email = models.EmailField(blank=True)
    website_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='community_actions/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title

    @property
    def participant_count(self):
        return self.participants.count()

    @property
    def is_full(self):
        return self.participant_count >= self.max_participants


class EcoTip(models.Model):
    """Environmental tips and best practices"""
    TIP_CATEGORIES = [
        ('transport', 'Transportation'),
        ('energy', 'Energy Conservation'),
        ('waste', 'Waste Reduction'),
        ('indoor', 'Indoor Air Quality'),
        ('outdoor', 'Outdoor Activities'),
        ('health', 'Health Protection'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=TIP_CATEGORIES)
    difficulty_level = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='easy'
    )
    estimated_impact = models.CharField(max_length=200, blank=True)  # e.g., "Reduces CO2 by 10%"
    is_featured = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, blank=True, related_name='liked_tips')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()


class UserEcoProfile(models.Model):
    """User's environmental engagement profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    actions_participated = models.PositiveIntegerField(default=0)
    actions_organized = models.PositiveIntegerField(default=0)
    carbon_footprint_goal = models.FloatField(default=0.0)  # kg CO2/year
    preferred_categories = models.ManyToManyField(PolicyCategory, blank=True)
    notification_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('never', 'Never'),
        ],
        default='weekly'
    )
    is_public_profile = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Eco Profile"


class PolicyFeedback(models.Model):
    """User feedback on policies and recommendations"""
    FEEDBACK_TYPES = [
        ('support', 'Support'),
        ('oppose', 'Oppose'),
        ('neutral', 'Neutral'),
        ('suggestion', 'Suggestion'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    policy = models.ForeignKey(EnvironmentalPolicy, on_delete=models.CASCADE)
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'policy']

    def __str__(self):
        return f"{self.user.username} - {self.policy.title} ({self.feedback_type})"