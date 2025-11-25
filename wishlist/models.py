from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError

# User Model Setup
User = get_user_model()

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin Panel Configuration
    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    # Show username to Admin panel & Python
    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    # Generate wishlist page URL
    def get_absolute_url(self):
        return reverse('wishlist_detail')

    # Items count property
    @property
    def items_count(self):
        return self.items.count()

    # Total price property
    @property
    def total_price(self):
        return sum(item.event.price for item in self.items.all() if item.event.price)

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    # Admin Panel Configuration
    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['wishlist', 'event']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.event.title} in {self.wishlist.user.username}'s wishlist"

    # Clean method to prevent duplicate items
    def clean(self):
        if WishlistItem.objects.filter(wishlist=self.wishlist, event=self.event).exists():
            raise ValidationError('This event is already in your wishlist.')

    # Save method to call clean
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)