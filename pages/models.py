from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Page(models.Model):
    PAGE_TYPES = (
        ('about', 'About Us'),
        ('how_it_works', 'How It Works'),
        ('contact', 'Contact Us'),
        ('faq', 'FAQ'),
        ('terms', 'Terms & Conditions'),
        ('privacy', 'Privacy Policy'),
        ('custom', 'Custom Page'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, default='custom')
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=False)
    show_in_navigation = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pages_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='pages_updated')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('pages:page_detail', kwargs={'slug': self.slug})


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=100, default='general')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['category', 'order', 'question']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question


class ContactSubmission(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('closed', 'Closed'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'

    def __str__(self):
        return f"{self.name} - {self.subject}"