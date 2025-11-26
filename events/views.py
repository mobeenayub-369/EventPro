from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import Event, EventImage, EventReview
from .forms import EventForm, EventImageForm


def event_list(request):
    """
    Display all active events with filtering and search functionality
    """
    # Get all active events
    events = Event.objects.filter(status='active').select_related('organizer').prefetch_related('images')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(event_type__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    # Filter by event type
    event_type = request.GET.get('event_type', '')
    if event_type:
        events = events.filter(event_type=event_type)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        events = events.filter(price__gte=min_price)
    if max_price:
        events = events.filter(price__lte=max_price)

    # Filter by capacity
    min_capacity = request.GET.get('min_capacity')
    if min_capacity:
        events = events.filter(capacity__gte=min_capacity)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['price', '-price', 'created_at', '-created_at', 'average_rating', '-average_rating']:
        events = events.order_by(sort_by)

    # Pagination
    paginator = Paginator(events, 12)  # Show 12 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'events': page_obj,
        'search_query': search_query,
        'event_type': event_type,
        'min_price': min_price,
        'max_price': max_price,
        'min_capacity': min_capacity,
        'sort_by': sort_by,
        'event_types': Event.EVENT_TYPE_CHOICES,
    }

    return render(request, 'events/event_list.html', context)


def event_detail(request, pk):
    """
    Display detailed view of a single event
    """
    event = get_object_or_404(
        Event.objects.select_related('organizer')
        .prefetch_related('images', 'reviews__user'),
        pk=pk,
        status='active'
    )

    # Increment view count
    event.increment_views()

    # Get related events (same category)
    related_events = Event.objects.filter(
        event_type=event.event_type,
        status='active'
    ).exclude(pk=pk)[:4]

    # Get approved reviews
    reviews = event.reviews.filter(is_approved=True)

    context = {
        'event': event,
        'related_events': related_events,
        'reviews': reviews,
        'average_rating': event.average_rating,
        'review_count': event.review_count,
    }

    return render(request, 'events/event_detail.html', context)


@login_required
def create_event(request):
    """
    Create a new event service
    """
    if request.method == 'POST':
        event_form = EventForm(request.POST)

        if event_form.is_valid():
            event = event_form.save(commit=False)
            event.organizer = request.user
            event.save()

            # Handle multiple image uploads
            primary_image = request.FILES.get('primary_image')
            if primary_image:
                EventImage.objects.create(
                    event=event,
                    image=primary_image,
                    is_primary=True,
                    display_order=0
                )

            # Handle additional images
            for i in range(2, 5):  # For image_2, image_3, image_4
                image_field = f'image_{i}'
                image_file = request.FILES.get(image_field)
                if image_file:
                    EventImage.objects.create(
                        event=event,
                        image=image_file,
                        is_primary=False,
                        display_order=i - 1
                    )

            messages.success(request, 'Event service created successfully!')
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        event_form = EventForm()

    context = {
        'event_form': event_form,
        'event_types': Event.EVENT_TYPE_CHOICES,
    }

    return render(request, 'events/create_event.html', context)


@login_required
def edit_event(request, pk):
    """
    Edit an existing event service
    """
    event = get_object_or_404(Event, pk=pk, organizer=request.user)

    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)

        if event_form.is_valid():
            event_form.save()

            # Handle image updates
            primary_image = request.FILES.get('primary_image')
            if primary_image:
                # Remove existing primary image
                EventImage.objects.filter(event=event, is_primary=True).delete()
                EventImage.objects.create(
                    event=event,
                    image=primary_image,
                    is_primary=True,
                    display_order=0
                )

            messages.success(request, 'Event service updated successfully!')
            return redirect('event_detail', pk=event.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        event_form = EventForm(instance=event)

    context = {
        'event_form': event_form,
        'event': event,
        'event_types': Event.EVENT_TYPE_CHOICES,
    }

    return render(request, 'events/edit_event.html', context)


@login_required
def my_events(request):
    """
    Display events created by the current user
    """
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')

    # Calculate stats
    total_events = events.count()
    active_events = events.filter(status='active').count()
    total_views = sum(event.view_count for event in events)
    total_bookings = sum(event.booking_count for event in events)

    context = {
        'events': events,
        'total_events': total_events,
        'active_events': active_events,
        'total_views': total_views,
        'total_bookings': total_bookings,
    }

    return render(request, 'events/my_events.html', context)


@login_required
def delete_event(request, pk):
    """
    Delete an event service
    """
    event = get_object_or_404(Event, pk=pk, organizer=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event service deleted successfully!')
        return redirect('my_events')

    return render(request, 'events/delete_event.html', {'event': event})