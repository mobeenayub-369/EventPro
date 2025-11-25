from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# Page Model for static content management
class Page(models.Model):
    # Status choices for pages
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Basic page information
    title = models.CharField(max_length=200, help_text="Enter the page title")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of the title")
    content = models.TextField(help_text="Main content of the page")

    # SEO and meta information
    meta_title = models.CharField(max_length=200, blank=True, help_text="SEO title tag")
    meta_description = models.TextField(blank=True, help_text="SEO meta description")

    # Page settings
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    show_in_footer = models.BooleanField(default=False, help_text="Display in footer navigation")
    show_in_header = models.BooleanField(default=False, help_text="Display in header navigation")
    order = models.IntegerField(default=0, help_text="Display order in navigation")

    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pages_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return self.title

    # Auto-generate slug from title
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # Check if page is published
    def is_published(self):
        return self.status == 'published'

    is_published.boolean = True
    is_published.short_description = 'Published'