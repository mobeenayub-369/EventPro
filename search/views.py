from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from events.models import Event
from accounts.models import CustomUser
from django.http import JsonResponse


def search_results(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', 'all')

    events = Event.objects.none()
    providers = CustomUser.objects.none()

    if query:
        # Base query for events
        event_query = Q(title__icontains=query) | Q(description__icontains=query)

        if category == 'all' or category == 'events':
            events = Event.objects.filter(event_query & Q(is_active=True))
            if category != 'all':
                events = events.filter(category__name=category)

        if category == 'all' or category == 'providers':
            providers = CustomUser.objects.filter(
                Q(username__icontains=query) |
                Q(business_name__icontains=query) |
                Q(skills__icontains=query) |
                Q(services_offered__icontains=query)
            ).filter(is_active=True, user_type='service_provider').distinct()

    # Pagination for events
    event_page = request.GET.get('event_page', 1)
    event_paginator = Paginator(events, 6)
    events_page = event_paginator.get_page(event_page)

    # Pagination for providers
    provider_page = request.GET.get('provider_page', 1)
    provider_paginator = Paginator(providers, 6)
    providers_page = provider_paginator.get_page(provider_page)

    context = {
        'query': query,
        'category': category,
        'events': events_page,
        'providers': providers_page,
        'event_count': events.count(),
        'provider_count': providers.count(),
        'total_results': events.count() + providers.count(),
    }

    return render(request, 'search/results.html', context)


def search_suggestions(request):
    """
    AJAX view for search suggestions (like Fiverr's autocomplete)
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = []

    # Event suggestions
    events = Event.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    ).filter(is_active=True)[:5]

    for event in events:
        suggestions.append({
            'type': 'Event',
            'title': event.title,
            'url': f'/events/{event.id}/',  # Simple URL
            'image': '/static/images/default-event.jpg'
        })

    # Service Provider suggestions
    providers = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(business_name__icontains=query) |
        Q(skills__icontains=query) |
        Q(services_offered__icontains=query)
    ).filter(is_active=True, user_type='service_provider')[:5]

    for provider in providers:
        suggestions.append({
            'type': 'Provider',
            'title': provider.business_name or provider.username,
            'url': f'/providers/{provider.id}/',  # Simple URL
            'image': '/static/images/default-profile.jpg'
        })

    return JsonResponse({'suggestions': suggestions})