from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.search import TrigramSimilarity

from .models import SearchQuery, PopularSearch
from events.models import Event  # ✅ Only Event import karein
from categories.models import Category  # ✅ Category alag app se import karein
from bookings.models import Booking


def search_events(request):
    """Advanced event search with filters"""
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    date = request.GET.get('date', '')
    location = request.GET.get('location', '')
    sort_by = request.GET.get('sort_by', 'relevance')

    # Start with all active events
    events = Event.objects.filter(is_active=True, is_approved=True)

    # Text search
    if query:
        # Using PostgreSQL full-text search if available
        events = events.annotate(
            search=SearchVector('title', 'description', 'organizer__username')
        ).filter(search=query)

        # Fallback to basic search
        if not events.exists():
            events = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(organizer__username__icontains=query) |
                Q(category__name__icontains=query)  # ✅ Yahan category model access ho raha hai
            ).filter(is_active=True, is_approved=True)

    # Apply filters
    if category:
        events = events.filter(category__slug=category)  # ✅ Yahan bhi category model

    # ... rest of the code remains same