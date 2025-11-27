from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event


class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=255)
    results_count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'

    def __str__(self):
        return f"{self.query} - {self.user.username if self.user else 'Anonymous'}"


class SearchFilter(models.Model):
    FILTER_TYPES = (
        ('category', 'Category'),
        ('price_range', 'Price Range'),
        ('date', 'Date'),
        ('location', 'Location'),
        ('rating', 'Rating'),
    )

    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='filters')
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPES)
    filter_value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.filter_type}: {self.filter_value}"


class PopularSearch(models.Model):
    query = models.CharField(max_length=255, unique=True)
    search_count = models.IntegerField(default=1)
    last_searched = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-search_count']
        verbose_name = 'Popular Search'
        verbose_name_plural = 'Popular Searches'

    def __str__(self):
        return f"{self.query} ({self.search_count})"

    def increment_count(self):
        self.search_count += 1
        self.last_searched = timezone.now()
        self.save()