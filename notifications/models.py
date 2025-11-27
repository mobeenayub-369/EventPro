from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('message', 'Message'),
        ('order', 'Order'),
        ('review', 'Review'),
        ('system', 'System'),
        ('promotion', 'Promotion'),
        ('reminder', 'Reminder'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_content_type = models.CharField(max_length=100, null=True, blank=True)
    action_url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        self.is_read = True
        self.save()


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_messages = models.BooleanField(default=True)
    email_orders = models.BooleanField(default=True)
    email_reviews = models.BooleanField(default=True)
    email_promotions = models.BooleanField(default=False)
    push_messages = models.BooleanField(default=True)
    push_orders = models.BooleanField(default=True)
    push_reviews = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences - {self.user.username}"