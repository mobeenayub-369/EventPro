from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('wedding', 'Wedding Event'),
        ('birthday', 'Birthday Party'),
        ('corporate', 'Corporate Event'),
        ('charity', 'Charity Event'),
        ('exhibition', 'Exhibition'),
        ('private', 'Private Party'),
        ('religious', 'Religious Event'),
        ('seminar', 'Seminar/Conference'),
        ('music', 'Music Concert'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    # Basic Information
    title = models.CharField(max_length=200, help_text="Enter a compelling title for your event service")
    description = models.TextField(help_text="Describe your event organization services in detail")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')

    # Event Type & Category
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='wedding')

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Starting price for your event service"
    )
    currency = models.CharField(max_length=3, default='USD')

    # Event Details
    capacity = models.PositiveIntegerField(
        default=50,
        help_text="Maximum number of attendees"
    )
    duration = models.PositiveIntegerField(
        default=4,
        help_text="Typical event duration in hours"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary service location or 'Multiple locations'"
    )

    # Status & Metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Service Metrics
    view_count = models.PositiveIntegerField(default=0)
    booking_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Event Service'
        verbose_name_plural = 'Event Services'

    def __str__(self):
        return f"{self.title} - {self.get_event_type_display()}"

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})

    def get_primary_image(self):
        return self.images.filter(is_primary=True).first()

    def get_display_price(self):
        return f"{self.currency} {self.price}"

    def increment_views(self):
        self.view_count += 1
        self.save()


class EventImage(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to='event_images/%Y/%m/%d/',
        help_text="Upload high-quality images of your event work"
    )
    caption = models.CharField(max_length=200, blank=True, help_text="Optional image caption")
    is_primary = models.BooleanField(
        default=False,
        help_text="Set as primary display image"
    )
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which images are displayed"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_primary', 'display_order', '-uploaded_at']
        verbose_name = 'Event Image'
        verbose_name_plural = 'Event Images'

    def __str__(self):
        return f"Image for {self.event.title}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset primary for other images of this event
        if self.is_primary:
            EventImage.objects.filter(event=self.event, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class EventReview(models.Model):
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.rating} stars for {self.event.title}"