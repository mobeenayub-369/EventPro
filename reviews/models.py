from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from events.models import Event
from django.utils import timezone


class Review(models.Model):
    """
    Review model for event ratings and comments.
    Similar to Fiverr's review system with ratings and responses.
    """

    RATING_CHOICES = [
        (1, '⭐ - Poor'),
        (2, '⭐⭐ - Fair'),
        (3, '⭐⭐⭐ - Good'),
        (4, '⭐⭐⭐⭐ - Very Good'),
        (5, '⭐⭐⭐⭐⭐ - Excellent'),
    ]

    # Review details
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Select rating from 1 (Poor) to 5 (Excellent)"
    )
    comment = models.TextField(
        max_length=1000,
        blank=True,
        help_text="Share your experience with this event (optional)"
    )

    # Review metadata
    is_verified = models.BooleanField(default=False, verbose_name="Verified Review")
    helpful_count = models.IntegerField(default=0, verbose_name="Helpful Votes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Response system (like Fiverr)
    organizer_response = models.TextField(
        max_length=1000,
        blank=True,
        verbose_name="Organizer Response"
    )
    response_created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta configuration for Review model."""
        unique_together = ['event', 'user']  # One review per user per event
        ordering = ['-created_at']  # Newest reviews first
        verbose_name = "Event Review"
        verbose_name_plural = "Event Reviews"

    def __str__(self):
        """String representation of the Review."""
        return f"{self.rating}★ Review for {self.event.title} by {self.user.username}"

    def get_rating_stars(self):
        """Return rating as stars for templates."""
        return '⭐' * self.rating + '☆' * (5 - self.rating)

    def get_rating_class(self):
        """Return CSS class based on rating."""
        rating_classes = {
            1: 'rating-poor',
            2: 'rating-fair',
            3: 'rating-good',
            4: 'rating-very-good',
            5: 'rating-excellent'
        }
        return rating_classes.get(self.rating, 'rating-good')

    def can_user_review(self, user):
        """Check if user can review this event."""
        # User should have attended the event to review (to be implemented with bookings)
        return True  # Temporary - integrate with bookings later

    def add_organizer_response(self, response_text):
        """Add organizer response to review."""
        self.organizer_response = response_text
        self.response_created_at = timezone.now()
        self.save()


class ReviewVote(models.Model):
    """
    Track helpful votes for reviews (like Fiverr's helpful system).
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'user']  # One vote per user per review
        verbose_name = "Review Vote"
        verbose_name_plural = "Review Votes"

    def __str__(self):
        vote_type = "Helpful" if self.is_helpful else "Not Helpful"
        return f"{vote_type} vote by {self.user.username} for review #{self.review.id}"