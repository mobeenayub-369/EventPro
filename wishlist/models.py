from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"Wishlist - {self.user.username}"

    @property
    def items_count(self):
        return self.items.count()

    @property
    def total_value(self):
        return sum(item.event.price for item in self.items.all() if item.event.price)


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['wishlist', 'event']
        ordering = ['-added_at']
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'

    def __str__(self):
        return f"{self.event.title} in {self.wishlist.user.username}'s wishlist"


class WishlistShare(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='shares')
    share_token = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Wishlist Share'
        verbose_name_plural = 'Wishlist Shares'

    def __str__(self):
        return f"Share - {self.wishlist.user.username}"

    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = self.generate_share_token()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)

    def generate_share_token(self):
        import uuid
        return f"WL{uuid.uuid4().hex[:12].upper()}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class WishlistNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_notifications')
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, choices=[
        ('price_drop', 'Price Drop'),
        ('available', 'Became Available'),
        ('reminder', 'Event Reminder'),
        ('almost_full', 'Almost Full'),
    ])
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wishlist Notification'
        verbose_name_plural = 'Wishlist Notifications'

    def __str__(self):
        return f"Notification - {self.user.username} - {self.event.title}"