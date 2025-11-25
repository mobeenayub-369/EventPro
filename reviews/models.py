from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


# Review Model
class Review(models.Model):
    # Review rating choices
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    # Review type choices
    REVIEW_TYPE_CHOICES = [
        ('event', 'Event Review'),
        ('organizer', 'Organizer Review'),
    ]

    # Basic review information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, related_name='reviews')

    # Review content
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, help_text="Brief summary of your review")
    comment = models.TextField(help_text="Detailed review of your experience")
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE_CHOICES, default='event')

    # Image fields for review
    image_1 = models.ImageField(upload_to='review_images/', blank=True, null=True, help_text="First review image")
    image_2 = models.ImageField(upload_to='review_images/', blank=True, null=True, help_text="Second review image")
    image_3 = models.ImageField(upload_to='review_images/', blank=True, null=True, help_text="Third review image")

    # Review status and verification
    is_verified = models.BooleanField(default=False, help_text="Verified purchase review")
    is_approved = models.BooleanField(default=True, help_text="Review approved for display")
    is_edited = models.BooleanField(default=False, help_text="Review has been edited")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(default=timezone.now, help_text="When the event was attended")

    # Admin moderation
    admin_notes = models.TextField(blank=True, help_text="Admin notes for moderation")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['user', 'event']  # One review per user per event
        indexes = [
            models.Index(fields=['event', 'rating']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['is_approved', 'created_at']),
        ]

    def __str__(self):
        return f"Review by {self.user.username} for {self.event.title} - {self.rating}/5"

    # Get star rating display
    def get_star_rating(self):
        return '★' * self.rating + '☆' * (5 - self.rating)

    # Get rating percentage for progress bars
    def get_rating_percentage(self):
        return (self.rating / 5) * 100

    # Check if user can edit review (within 7 days)
    def can_edit(self):
        return (timezone.now() - self.created_at).days <= 7

    # Check if user attended the event
    def is_verified_attendee(self):
        return self.user.bookings.filter(
            event=self.event,
            status='confirmed'
        ).exists()

    # Get all review images
    def get_review_images(self):
        images = []
        if self.image_1:
            images.append(self.image_1)
        if self.image_2:
            images.append(self.image_2)
        if self.image_3:
            images.append(self.image_3)
        return images

    # Check if review has images
    def has_images(self):
        return bool(self.image_1 or self.image_2 or self.image_3)


# Review Response Model (for organizers to respond)
class ReviewResponse(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses')
    response_text = models.TextField(help_text="Organizer's response to the review")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review Response'
        verbose_name_plural = 'Review Responses'

    def __str__(self):
        return f"Response to review #{self.review.id}"


# Review Report Model (for reporting inappropriate reviews)
class ReviewReport(models.Model):
    REPORT_REASONS = [
        ('spam', 'Spam or misleading'),
        ('inappropriate', 'Inappropriate content'),
        ('harassment', 'Harassment or hate speech'),
        ('false_info', 'False information'),
        ('other', 'Other'),
    ]

    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(help_text="Additional details about the report")

    # Report status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('investigating', 'Under Investigation'),
            ('resolved', 'Resolved'),
            ('dismissed', 'Dismissed'),
        ],
        default='pending'
    )

    # Admin fields
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='resolved_reports')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review Report'
        verbose_name_plural = 'Review Reports'
        unique_together = ['review', 'reporter']  # One report per user per review

    def __str__(self):
        return f"Report on review #{self.review.id} by {self.reporter.username}"