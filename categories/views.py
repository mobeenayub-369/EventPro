from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Category, Tag
from events.models import Event


# List Active Categories with Image Support
def category_list(request):
    """
    Display all active categories with their images and event counts
    Optimized query with image URL handling
    """
    # IMAGE UPLOAD: Get categories with event counts and image support
    categories = Category.objects.filter(is_active=True).annotate(
        events_count=Count('event')
    ).order_by('name')

    return render(request, 'categories/category_list.html', {
        'categories': categories
    })


# Specific Category Events with Image Support
def category_events(request, category_slug):
    """
    Display events for a specific category with category image
    Includes error handling for missing categories
    """
    # IMAGE UPLOAD: Get category with image and related events
    category = get_object_or_404(Category, slug=category_slug, is_active=True)

    # Get active events for this category
    events = Event.objects.filter(category=category, is_active=True).select_related(
        'organizer', 'category'
    ).order_by('-created_at')

    return render(request, 'categories/category_events.html', {
        'category': category,
        'events': events
    })


# Specific Events by Tags with Error Handling
def tag_events(request, tag_slug):
    """
    Display events for a specific tag
    Fixed the tag filtering issue in the original code
    """
    tag = get_object_or_404(Tag, slug=tag_slug)

    # FIX: Corrected filter from 'tags_slug' to proper ManyToMany relationship
    events = Event.objects.filter(tags__slug=tag_slug, is_active=True).select_related(
        'organizer', 'category'
    ).order_by('-created_at')

    return render(request, 'categories/tag_events.html', {
        'tag': tag,
        'events': events
    })


# Tag List request with Count
def tag_list(request):
    """
    Display all tags with their event counts
    """
    # IMAGE UPLOAD: Get tags with event counts
    tags = Tag.objects.annotate(
        events_count=Count('event')
    ).order_by('name')

    return render(request, 'categories/tag_list.html', {
        'tags': tags
    })