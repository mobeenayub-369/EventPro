from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Event, EventImage
from .forms import EventForm, EventImageForm
from categories.models import Category


# Event List View with Enhanced Search and Image Support
def event_list(request):
    """
    Display all active events with search, filtering, and image support
    Optimized queries for better performance
    """
    # Base queryset with image optimization
    events = Event.objects.filter(is_active=True).select_related(
        'organizer', 'category'
    ).prefetch_related('tags').order_by('-created_at')

    # Search Functionality with improved query
    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(title__icontains=query) |  # FIXED: Corrected typo 'title_icontains'
            Q(description__icontains=query) |  # FIXED: Corrected typo 'description_icontains'
            Q(location__icontains=query)  # FIXED: Corrected typo 'location_icontains'
        )

    # Category Filter with proper field name
    category_slug = request.GET.get('category')
    if category_slug:
        events = events.filter(category__slug=category_slug)  # FIXED: Corrected 'category_slug' to 'category__slug'

    # Featured Filter
    featured = request.GET.get('featured')
    if featured:
        events = events.filter(is_featured=True)

    # Categories Fetch for filter dropdown
    categories = Category.objects.filter(is_active=True)

    context = {
        'events': events,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
        'featured_only': bool(featured)
    }

    return render(request, 'events/event_list.html', context)


# Event Detail View with Enhanced Image Gallery
def event_detail(request, slug):
    """
    Display event details with comprehensive image media and related events
    """
    event = get_object_or_404(
        Event.objects.select_related('organizer', 'category')
        .prefetch_related('tags', 'gallery_images'),
        slug=slug,
        is_active=True
    )

    # Related Events with image optimization
    related_events = Event.objects.filter(
        category=event.category,
        is_active=True
    ).exclude(id=event.id).select_related('category')[:4]

    context = {
        'event': event,
        'related_events': related_events
    }

    return render(request, 'events/event_detail.html', context)


# Create Event View with Comprehensive Image Handling
@login_required
def create_event(request):
    """
    Handle event creation with multiple image upload support
    Includes proper file handling and error management
    """
    if request.method == 'POST':
        # IMAGE UPLOAD: request.FILES is essential for image uploads
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                event = form.save(commit=False)
                event.organizer = request.user
                event.save()

                # Save Many-to-Many relationships
                form.save_m2m()

                # IMAGE UPLOAD: Success message with image info
                if any([event.main_image, event.thumbnail, event.image]):
                    messages.success(request, 'Event created successfully with images!')
                else:
                    messages.success(request, 'Event created successfully!')

                return redirect('event_detail', slug=event.slug)

            except Exception as e:
                messages.error(request, f'Error creating event: {str(e)}')
        else:
            # Form validation failed
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})


# Edit Event View with Image Management
@login_required
def edit_event(request, slug):
    """
    Handle event editing with image update support
    Only allows event organizer to edit their events
    """
    event = get_object_or_404(Event, slug=slug, organizer=request.user)

    if request.method == 'POST':
        # IMAGE UPLOAD: Include request.FILES for image updates
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            try:
                form.save()

                # IMAGE UPLOAD: Check if any images were updated
                image_updated = any([
                    'main_image' in request.FILES,
                    'thumbnail' in request.FILES,
                    'image' in request.FILES
                ])

                if image_updated:
                    messages.success(request, 'Event updated successfully with new images!')
                else:
                    messages.success(request, 'Event updated successfully!')

                return redirect('event_detail', slug=event.slug)

            except Exception as e:
                messages.error(request, f'Error updating event: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


# Delete Event View with Image Cleanup
@login_required
def delete_event(request, slug):
    """
    Handle event deletion with proper confirmation
    Only allows event organizer to delete their events
    """
    event = get_object_or_404(Event, slug=slug, organizer=request.user)

    # Delete confirmation
    if request.method == 'POST':
        try:
            event_title = event.title
            event.delete()
            messages.success(request, f'Event "{event_title}" deleted successfully!')
            return redirect('event_list')
        except Exception as e:
            messages.error(request, f'Error deleting event: {str(e)}')
            return redirect('event_detail', slug=slug)

    # Show confirmation page
    return render(request, 'events/delete_event.html', {'event': event})


# My Events View with Enhanced Display
@login_required
def my_events(request):
    """
    Display events created by the current user with statistics
    """
    # FIXED: Corrected context variable name from 'events: events' to 'events': events
    events = Event.objects.filter(organizer=request.user).select_related(
        'category'
    ).prefetch_related('bookings').order_by('-created_at')

    return render(request, 'events/my_events.html', {'events': events})


# IMAGE UPLOAD: View for adding media images
@login_required
def add_event_images(request, slug):
    """
    Handle addition of media images to existing events
    Only allows event organizer to add images
    """
    event = get_object_or_404(Event, slug=slug, organizer=request.user)

    if request.method == 'POST':
        form = EventImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                event_image = form.save()
                event.gallery_images.add(event_image)
                messages.success(request, 'Image added to event media successfully!')
                return redirect('event_detail', slug=event.slug)
            except Exception as e:
                messages.error(request, f'Error adding image: {str(e)}')
        else:
            messages.error(request, 'Please correct the image upload errors.')
    else:
        form = EventImageForm()

    return render(request, 'events/add_event_images.html', {
        'form': form,
        'event': event
    })