from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard')
    last_visited = models.DateTimeField(default=timezone.now)
    preferred_view = models.CharField(
        max_length=20,
        choices=[
            ('overview', 'Overview'),
            ('analytics', 'Analytics'),
            ('simple', 'Simple View'),
        ],
        default='overview'
    )

    class Meta:
        verbose_name = 'User Dashboard'
        verbose_name_plural = 'User Dashboards'

    def __str__(self):
        return f"Dashboard - {self.user.username}"

    def update_last_visited(self):
        self.last_visited = timezone.now()
        self.save()


class DashboardWidget(models.Model):
    WIDGET_TYPES = (
        ('stats', 'Statistics'),
        ('chart', 'Chart'),
        ('recent', 'Recent Activity'),
        ('quick_actions', 'Quick Actions'),
        ('notifications', 'Notifications'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=100)
    position = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        unique_together = ['user', 'widget_type']

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('login', 'User Login'),
        ('event_view', 'Event Viewed'),
        ('event_created', 'Event Created'),
        ('booking_made', 'Booking Made'),
        ('payment_made', 'Payment Made'),
        ('review_added', 'Review Added'),
        ('message_sent', 'Message Sent'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class DashboardMetric(models.Model):
    METRIC_TYPES = (
        ('events_created', 'Events Created'),
        ('bookings_made', 'Bookings Made'),
        ('revenue_generated', 'Revenue Generated'),
        ('messages_sent', 'Messages Sent'),
        ('reviews_given', 'Reviews Given'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    period = models.CharField(max_length=10)  # daily, weekly, monthly
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.user.username} - {self.metric_type} - {self.period}"