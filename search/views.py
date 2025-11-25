from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from events.models import Event
from categories.models import Category, Tag


User = get_user_model()


# Advanced Search View
def advanced_search(request):
    # Get search parameters
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    tags = request.GET.getlist('tags')
    location = request.GET.get('location', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    event_type = request.GET.get('event_type', '')
    sort_by = request.GET.get('sort_by', 'relevance')

    # Start with all active events
    events = Event.objects.filter(is_active=True).select_related('organizer', 'category')

    # Apply search filters
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(organizer__username__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()

    # Category filter
    if category:
        events = events.filter(category__slug=category)

    # Tags filter
    if tags:
        events = events.filter(tags__slug__in=tags).distinct()

    # Location filter
    if location:
        events = events.filter(location__icontains=location)

    # Date range filter
    if date_from:
        events = events.filter(date__gte=date_from)
    if date_to:
        events = events.filter(date__lte=date_to)

    # Price range filter - Convert to float safely
    if price_min:
        try:
            events = events.filter(price__gte=float(price_min))
        except (ValueError, TypeError):
            pass

    if price_max:
        try:
            events = events.filter(price__lte=float(price_max))
        except (ValueError, TypeError):
            pass

    # Event type filter
    if event_type:
        if event_type == 'free':
            events = events.filter(price=0)
        elif event_type == 'paid':
            events = events.filter(price__gt=0)
        elif event_type == 'featured':
            events = events.filter(is_featured=True)

    # Sorting
    if sort_by == 'date_asc':
        events = events.order_by('date', 'time')
    elif sort_by == 'date_desc':
        events = events.order_by('-date', '-time')
    elif sort_by == 'price_asc':
        events = events.order_by('price')
    elif sort_by == 'price_desc':
        events = events.order_by('-price')
    elif sort_by == 'popular':
        #  Use annotation for booking count
        events = events.annotate(booking_count=Count('bookings')).order_by('-booking_count')
    else:  # relevance or default
        events = events.order_by('-is_featured', '-created_at')

    # Get filter options
    categories = Category.objects.filter(is_active=True)
    popular_tags = Tag.objects.filter(events__is_active=True).distinct()[:20]

    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_events = paginator.get_page(page_number)

    context = {
        'events': page_events,
        'query': query,
        'categories': categories,
        'popular_tags': popular_tags,
        'filters': {
            'category': category,
            'tags': tags,
            'location': location,
            'date_from': date_from,
            'date_to': date_to,
            'price_min': price_min,
            'price_max': price_max,
            'event_type': event_type,
            'sort_by': sort_by,
        },
        'total_results': paginator.count,
        'title': f"Search Results{' for ' + query if query else ''}"
    }

    return render(request, 'search/advanced_search.html', context)


# Quick Search View (for AJAX requests)
def quick_search(request):
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    # Search events
    events = Event.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query),
        is_active=True
    ).select_related('category')[:5]

    # Search categories
    categories = Category.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query),
        is_active=True
    )[:3]

    # Safe organizer search - check if user_type field exists
    try:
        organizers = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            is_active=True
        )
        # Filter organizers if user_type field exists
        if hasattr(User, 'user_type'):
            organizers = organizers.filter(user_type='organizer')
        organizers = organizers[:3]
    except Exception:
        organizers = []

    # Format results
    results = []

    # Add events
    for event in events:
        results.append({
            'type': 'event',
            'title': event.title,
            'description': f"{event.category.name if event.category else 'Event'} • {event.location}",
            'url': event.get_absolute_url(),
            'image': event.image.url if event.image else None,
            'date': event.date.strftime('%b %d, %Y'),
            'price': f"Rs. {event.price}" if event.price > 0 else 'Free'
        })

    # Add categories
    for category in categories:
        results.append({
            'type': 'category',
            'title': category.name,
            'description': f"Category • {category.events.count()} events",
            'url': f"/events/?category={category.slug}",
            'image': category.image.url if category.image else None
        })

    # Add organizers
    for organizer in organizers:
        results.append({
            'type': 'organizer',
            'title': organizer.get_full_name() or organizer.username,
            'description': 'Event Organizer',
            'url': f"/organizer/{organizer.username}/",
            'image': organizer.profile_picture.url if hasattr(organizer,
                                                              'profile_picture') and organizer.profile_picture else None
        })

    return JsonResponse({'results': results})


# Search Suggestions View
def search_suggestions(request):
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = []

    # Event title suggestions
    event_titles = Event.objects.filter(
        title__icontains=query,
        is_active=True
    ).values_list('title', flat=True).distinct()[:5]

    for title in event_titles:
        suggestions.append({
            'text': title,
            'type': 'event',
            'category': 'Events'
        })

    # Category suggestions
    category_names = Category.objects.filter(
        name__icontains=query,
        is_active=True
    ).values_list('name', flat=True).distinct()[:3]

    for name in category_names:
        suggestions.append({
            'text': name,
            'type': 'category',
            'category': 'Categories'
        })

    # Location suggestions
    locations = Event.objects.filter(
        location__icontains=query,
        is_active=True
    ).values_list('location', flat=True).distinct()[:3]

    for location in locations:
        suggestions.append({
            'text': location,
            'type': 'location',
            'category': 'Locations'
        })

    # Tag suggestions
    tags = Tag.objects.filter(
        name__icontains=query
    ).values_list('name', flat=True).distinct()[:3]

    for tag in tags:
        suggestions.append({
            'text': tag,
            'type': 'tag',
            'category': 'Tags'
        })

    return JsonResponse({'suggestions': suggestions})


# Filter Events by Category
def category_events(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    events = Event.objects.filter(category=category, is_active=True).select_related('organizer')

    # Get similar categories
    similar_categories = Category.objects.filter(
        is_active=True
    ).exclude(slug=category_slug)[:4]

    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_events = paginator.get_page(page_number)

    context = {
        'category': category,
        'events': page_events,
        'similar_categories': similar_categories,
        'total_results': paginator.count,
        'title': f"Events in {category.name}"
    }

    return render(request, 'search/category_events.html', context)


# Filter Events by Tag
def tag_events(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    events = Event.objects.filter(tags=tag, is_active=True).select_related('organizer', 'category')

    # Get related tags
    related_tags = Tag.objects.filter(
        events__tags=tag
    ).exclude(slug=tag_slug).distinct()[:8]

    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_events = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'events': page_events,
        'related_tags': related_tags,
        'total_results': paginator.count,
        'title': f"Events tagged with #{tag.name}"
    }

    return render(request, 'search/tag_events.html', context)