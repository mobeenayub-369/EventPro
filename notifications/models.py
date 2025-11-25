from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

# USER MODEL SETUP
User = get_user_model()

class Notification(models.Model):

    NOTIFICATION_TYPES = (
        ('booking_created', 'New Booking'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('event_created', 'New Event'),
        ('message_received', 'New Message'),
        ('system_alert', 'System Alert'),
    )


    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    # META CLASS (Admin panel configuration)
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'


    # STRING METHOD
    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}"

    # REDIRECT AFTER CLICKING NOTIFICATION
    def get_absolute_url(self):
        if self.related_object_type == 'booking' and self.related_object_id:
            return reverse('booking_detail', kwargs={'booking_id': self.related_object_id})
        elif self.related_object_type == 'event' and self.related_object_id:
            return reverse('event_detail',
                           kwargs={'slug': 'event-slug'})
        elif self.related_object_type == 'message' and self.related_object_id:
            return reverse('thread_detail', kwargs={'thread_id': self.related_object_id})
        else:
            return reverse('notifications_list')


    def mark_as_read(self):
        self.is_read = True
        self.save()


    # RETURN APPROPRIATE ICON BY THE TYPE OF NOTIFICATION
    def get_icon(self):
        icons = {
            'booking_created': 'fas fa-ticket-alt',
            'booking_confirmed': 'fas fa-check-circle',
            'booking_cancelled': 'fas fa-times-circle',
            'event_created': 'fas fa-calendar-plus',
            'message_received': 'fas fa-envelope',
            'system_alert': 'fas fa-bell',
        }
        return icons.get(self.notification_type, 'fas fa-bell')


    # RETURN COLORS BY THE TYPE OF NOTIFICATIONS
    def get_color(self):
        colors = {
            'booking_created': 'var(--primary)',
            'booking_confirmed': 'var(--success)',
            'booking_cancelled': 'var(--danger)',
            'event_created': 'var(--info)',
            'message_received': 'var(--warning)',
            'system_alert': 'var(--secondary)',
        }
        return colors.get(self.notification_type, 'var(--secondary)')
