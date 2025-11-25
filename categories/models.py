from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """
    Category Model for organizing events with image upload functionality
    Each category can have an image for better visual representation
    """
    name = models.CharField(max_length=100, unique=True,
                            help_text="Enter category name (e.g., Music, Sports, Business)")
    slug = models.SlugField(max_length=100, unique=True, help_text="URL-friendly version of the name (auto-generated)")
    description = models.TextField(blank=True, help_text="Brief description of the category")

    # IMAGE UPLOAD: Category image with organized folder structure and validation
    image = models.ImageField(
        upload_to='categories/%Y/%m/%d/',  # Organize by year/month/day for better file management
        blank=True,
        null=True,
        help_text="Upload category image (Recommended: 400x300 pixels, Max: 2MB)",
        verbose_name="Category Image"
    )

    is_active = models.BooleanField(default=True, help_text="Enable/disable category visibility")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin Panel configuration
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    # IMAGE UPLOAD: Auto-generate slug from name if not provided
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from name if not provided
        This ensures every category has a URL-friendly slug
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # Generate URL of category
    def get_absolute_url(self):
        return reverse('category_events', kwargs={'category_slug': self.slug})

    # IMAGE UPLOAD: Property to safely get image URL
    @property
    def image_url(self):
        """
        Returns the category image URL if exists, otherwise returns None
        This prevents template errors when image is not available
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

    # IMAGE UPLOAD: Property to check if category has image
    @property
    def has_image(self):
        """Check if category has an uploaded image"""
        return bool(self.image)


# Tag Model for event tagging
class Tag(models.Model):
    """
    Tag Model for categorizing events with keywords
    Tags help in better event discovery and filtering
    """
    name = models.CharField(max_length=50, unique=True, help_text="Enter tag name (e.g., concert, workshop, free)")
    slug = models.SlugField(max_length=50, unique=True, help_text="URL-friendly version of the tag name")
    description = models.TextField(blank=True, help_text="Brief description of the tag")
    created_at = models.DateTimeField(auto_now_add=True)

    # Sorting by names
    class Meta:
        ordering = ['name']

    # Show tag name in Admin-panel
    def __str__(self):
        return self.name

    # IMAGE UPLOAD: Auto-generate slug from name if not provided
    def save(self, *args, **kwargs):
        """
        Auto-generate slug from tag name if not provided
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tag_events', kwargs={'tag_slug': self.slug})

    # IMAGE UPLOAD: Property to get events count (useful for templates)
    @property
    def events_count(self):
        """Return count of events associated with this tag"""
        return self.event_set.count()