from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Model representing different types of events in the system.
    Uses FontAwesome icons for visual representation.
    """

    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="URL Slug")
    description = models.TextField(blank=True, verbose_name="Category Description")

    # Only icon field - no image field
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='fas fa-calendar-alt',
        verbose_name="FontAwesome Icon",
        help_text="e.g., fas fa-ring, fas fa-briefcase, fas fa-birthday-cake"
    )

    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_icon_class(self):
        """Return icon class with fallback to default."""
        return self.icon if self.icon else 'fas fa-calendar-alt'