from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User Model extending Django's AbstractUser
class CustomUser(AbstractUser):
    # User type choices for different roles in the system
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('organizer', 'Event Organizer'),
    )

    # User profile fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # IMAGE UPLOAD: Profile picture field with custom upload path and optimized settings
    profile_picture = models.ImageField(
        upload_to='profiles/%Y/%m/%d/',  # Organized folder structure by year/month/day
        blank=True,
        null=True,
        help_text='Upload a profile picture (Recommended: 200x200 pixels)'
    )

    bio = models.TextField(max_length=150, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # FIX: Override groups field to resolve reverse accessor clash with default User model
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',  # Unique related_name to avoid clash
        related_query_name='customuser',
    )

    # FIX: Override user_permissions field to resolve reverse accessor clash
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # Unique related_name to avoid clash
        related_query_name='customuser',
    )

    def __str__(self):
        return self.username

    # PROPERTY: Get profile picture URL or default avatar
    @property
    def profile_picture_url(self):
        """
        Returns the profile picture URL if exists, otherwise returns None
        This property can be used in templates to safely access the image URL
        """
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return None


# User Profile Model for additional user information
class UserProfile(models.Model):
    # One-to-one relationship with CustomUser
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # Social media links
    website = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"