from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Sum
from django.utils.text import slugify
import os

# User Model Setup
User = get_user_model()


class Event(models.Model):
    """
    Event Model with comprehensive image upload functionality
    Supports multiple image types: main image, thumbnails, and media images
    """
    title = models.CharField(max_length=200, help_text="Enter a catchy title for your event")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of the title")
    description = models.TextField(help_text="Detailed description of your event")

    # IMAGE UPLOAD: Main event image with organized storage
    main_image = models.ImageField(
        upload_to='events/main_images/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Main event banner image (Recommended: 1200x600px, Max: 5MB)",
        verbose_name="Main Event Image"
    )

    # IMAGE UPLOAD: Thumbnail for event listings
    thumbnail = models.ImageField(
        upload_to='events/thumbnails/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Event thumbnail for cards and lists (Recommended: 400x300px, Max: 2MB)",
        verbose_name="Event Thumbnail"
    )

    # BACKWARD COMPATIBILITY: Original image field for existing data
    image = models.ImageField(
        upload_to='events/original/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Original event image (fallback)",
        verbose_name="Event Image"
    )

    # Event details
    date = models.DateField(help_text="Date when the event will take place")
    time = models.TimeField(help_text="Start time of the event")
    location = models.CharField(max_length=300, help_text="Venue or online location")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Ticket price in Rs.")
    capacity = models.PositiveIntegerField(help_text="Maximum number of attendees")

    # Relationships
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_events')
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('categories.Tag', blank=True)

    # Status flags
    is_active = models.BooleanField(default=True, help_text="Make event visible to public")
    is_featured = models.BooleanField(default=False, help_text="Feature this event on homepage")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # IMAGE UPLOAD: Gallery images for multiple event photos
    gallery_images = models.ManyToManyField(
        'EventImage',
        blank=True,
        related_name='events',
        help_text="Additional images for event media"
    )

    # Admin Panel Configuration
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['date', 'time']),
        ]

    def __str__(self):
        return self.title

    # IMAGE UPLOAD: Auto-generate slug from title
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from title if not provided
        Ensures URL-friendly event links
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})

    # Calculate available seats
    def available_seats(self):
        """
        Calculate remaining available seats for the event
        Useful for booking management and availability display
        """
        booked_seats = self.bookings.aggregate(total=Sum('ticket_count'))['total'] or 0
        return max(0, self.capacity - booked_seats)

    # Check Available Seats
    def is_available(self):
        """
        Check if event has available seats and is active
        Used for booking eligibility
        """
        return self.available_seats() > 0 and self.is_active

    # IMAGE UPLOAD: Method to get display image with priority
    def get_display_image(self):
        """
        Get the best available image for display with fallback priority
        Priority: main_image > image > thumbnail
        """
        if self.main_image and hasattr(self.main_image, 'url'):
            return self.main_image.url
        elif self.image and hasattr(self.image, 'url'):
            return self.image.url
        elif self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        return None

    # IMAGE UPLOAD: Check if event has any images
    def has_images(self):
        """
        Check if event has any uploaded images
        Useful for template conditional rendering
        """
        return bool(self.main_image or self.image or self.thumbnail or self.gallery_images.exists())

    # IMAGE UPLOAD: Get all event images for media display
    def get_all_images(self):
        """
        Get all images associated with this event for media
        Returns list of image objects with metadata
        """
        images = []

        if self.main_image:
            images.append({
                'image': self.main_image,
                'url': self.main_image.url,
                'type': 'main',
                'caption': 'Main Event Image'
            })

        if self.image and self.image != self.main_image:
            images.append({
                'image': self.image,
                'url': self.image.url,
                'type': 'original',
                'caption': 'Event Image'
            })

        if self.thumbnail and self.thumbnail != self.main_image and self.thumbnail != self.image:
            images.append({
                'image': self.thumbnail,
                'url': self.thumbnail.url,
                'type': 'thumbnail',
                'caption': 'Event Thumbnail'
            })

        # Add media images with captions
        for gallery_image in self.gallery_images.all().order_by('uploaded_at'):
            images.append({
                'image': gallery_image.image,
                'url': gallery_image.image.url,
                'type': 'media',
                'caption': gallery_image.caption or 'Gallery Image',
                'uploaded_at': gallery_image.uploaded_at
            })

        return images

    # IMAGE UPLOAD: Property for template usage
    @property
    def display_image_url(self):
        """Property to safely get display image URL in templates"""
        return self.get_display_image()

    @property
    def image_count(self):
        """Count of all images associated with this event"""
        return len(self.get_all_images())


# IMAGE UPLOAD: EventImage Model for multiple media images
class EventImage(models.Model):
    """
    Model for storing additional event media images
    Supports captions and organized storage
    """
    image = models.ImageField(
        upload_to='events/media/%Y/%m/%d/',
        help_text="Additional event photo for media (Recommended: 800x600px, Max: 5MB)"
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional description for this image"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Event Image'
        verbose_name_plural = 'Event Images'

    def __str__(self):
        if self.caption:
            return f"Gallery Image: {self.caption}"
        return f"Gallery Image {self.id}"

    # IMAGE UPLOAD: Property to get filename
    @property
    def filename(self):
        """Get the original filename of the uploaded image"""
        return os.path.basename(self.image.name) if self.image else ""

    # IMAGE UPLOAD: Property to check if image exists
    @property
    def has_image(self):
        """Check if this media entry has an uploaded image"""
        return bool(self.image and hasattr(self.image, 'url'))