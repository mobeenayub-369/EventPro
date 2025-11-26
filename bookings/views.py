from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Booking, BookingMessage, BookingRevision
from .forms import BookingForm, BookingMessageForm, BookingRevisionForm


@login_required
def create_booking(request, event_id):
    """
    Create a new booking for an event
    """
    from events.models import Event

    event = get_object_or_404(Event, pk=event_id, status='active')

    # Check if user is trying to book their own event
    if event.organizer == request.user:
        messages.error(request, "You cannot book your own event service.")
        return redirect('events:event_detail', pk=event_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.service_provider = event.organizer
            booking.event = event
            booking.base_price = event.price

            # Calculate total amount
            booking.total_amount = (
                    booking.base_price +
                    booking.additional_charges -
                    booking.discount_amount
            )

            booking.save()

            # Send notification to service provider
            messages.success(
                request,
                f"Booking request sent to {event.organizer.username}! "
                "They will respond within 24 hours."
            )

            return redirect('bookings:booking_detail', pk=booking.pk)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Pre-fill form with event details
        initial_data = {
            'event_date': timezone.now().date(),
            'event_duration': event.duration,
            'number_of_guests': min(event.capacity, 50),
            'base_price': event.price,
            'total_amount': event.price,
        }
        form = BookingForm(initial=initial_data)

    context = {
        'form': form,
        'event': event,
        'title': f'Book {event.title}'
    }

    return render(request, 'bookings/create_booking.html', context)


@login_required
def booking_detail(request, pk):
    """
    View booking details
    """
    booking = get_object_or_404(
        Booking.objects.select_related('client', 'service_provider', 'event'),
        pk=pk
    )

    # Check if user has permission to view this booking
    if request.user not in [booking.client, booking.service_provider]:
        messages.error(request, "You don't have permission to view this booking.")
        return redirect('bookings:booking_list')

    # Mark messages as read
    if request.user != booking.client:
        booking.messages.filter(is_read=False).update(is_read=True)

    # Forms for messaging and revisions
    message_form = BookingMessageForm()
    revision_form = BookingRevisionForm()

    # Get messages and revisions
    messages = booking.messages.select_related('sender').all()
    revisions = booking.revisions.select_related('requested_by').all()

    context = {
        'booking': booking,
        'messages': messages,
        'revisions': revisions,
        'message_form': message_form,
        'revision_form': revision_form,
        'timeline': booking.get_timeline_status(),
    }

    return render(request, 'bookings/booking_detail.html', context)


@login_required
def booking_list(request):
    """
    List all bookings for the current user
    """
    # Get bookings where user is either client or provider
    bookings = Booking.objects.filter(
        Q(client=request.user) | Q(service_provider=request.user)
    ).select_related('client', 'service_provider', 'event').order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(booking_status=status_filter)

    # Filter by role (client/provider)
    role_filter = request.GET.get('role', '')
    if role_filter == 'client':
        bookings = bookings.filter(client=request.user)
    elif role_filter == 'provider':
        bookings = bookings.filter(service_provider=request.user)

    # Pagination
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(booking_status='pending').count()
    confirmed_bookings = bookings.filter(booking_status='confirmed').count()
    completed_bookings = bookings.filter(booking_status='completed').count()

    context = {
        'bookings': page_obj,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'status_choices': Booking.BOOKING_STATUS_CHOICES,
    }

    return render(request, 'bookings/booking_list.html', context)


@login_required
def update_booking_status(request, pk, action):
    """
    Update booking status (confirm, cancel, complete, etc.)
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Check permissions
    if request.user not in [booking.client, booking.service_provider]:
        messages.error(request, "You don't have permission to update this booking.")
        return redirect('bookings:booking_list')

    # Define allowed actions for each role
    provider_actions = ['confirm', 'reject', 'start', 'complete']
    client_actions = ['cancel']

    if (request.user == booking.service_provider and action not in provider_actions) or \
            (request.user == booking.client and action not in client_actions):
        messages.error(request, "You cannot perform this action.")
        return redirect('bookings:booking_detail', pk=pk)

    # Update status based on action
    if action == 'confirm' and request.user == booking.service_provider:
        booking.booking_status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()
        messages.success(request, "Booking confirmed successfully!")

    elif action == 'reject' and request.user == booking.service_provider:
        booking.booking_status = 'rejected'
        booking.save()
        messages.info(request, "Booking request rejected.")

    elif action == 'cancel' and request.user == booking.client:
        if booking.can_be_cancelled():
            booking.booking_status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            messages.info(request, "Booking cancelled successfully.")
        else:
            messages.error(request, "This booking cannot be cancelled.")

    elif action == 'start' and request.user == booking.service_provider:
        booking.booking_status = 'in_progress'
        booking.save()
        messages.success(request, "Event marked as in progress.")

    elif action == 'complete' and request.user == booking.service_provider:
        booking.booking_status = 'completed'
        booking.completed_at = timezone.now()
        booking.save()
        messages.success(request, "Event marked as completed!")

    return redirect('bookings:booking_detail', pk=pk)


@login_required
def send_booking_message(request, pk):
    """
    Send a message for a booking
    """
    booking = get_object_or_404(Booking, pk=pk)

    # Check permissions
    if request.user not in [booking.client, booking.service_provider]:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        form = BookingMessageForm(request.POST, request.FILES)

        if form.is_valid():
            message = form.save(commit=False)
            message.booking = booking
            message.sender = request.user
            message.save()

            return JsonResponse({
                'success': True,
                'message': 'Message sent successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def request_booking_revision(request, pk):
    """
    Request a revision for a booking
    """
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        form = BookingRevisionForm(request.POST)

        if form.is_valid():
            revision = form.save(commit=False)
            revision.booking = booking
            revision.requested_by = request.user
            revision.save()

            messages.success(request, "Revision request sent successfully!")
            return redirect('bookings:booking_detail', pk=pk)
        else:
            messages.error(request, "Please correct the errors below.")

    return redirect('bookings:booking_detail', pk=pk)


@login_required
def booking_calendar(request):
    """
    Calendar view for bookings
    """
    # Get user's bookings (as client or provider)
    user_bookings = Booking.objects.filter(
        Q(client=request.user) | Q(service_provider=request.user)
    ).filter(
        booking_status__in=['confirmed', 'in_progress']
    ).select_related('event', 'client', 'service_provider')

    # Format for calendar
    calendar_events = []
    for booking in user_bookings:
        calendar_events.append({
            'title': f"{booking.event.title} - {booking.get_booking_status_display()}",
            'start': f"{booking.event_date}T{booking.event_time}",
            'end': f"{booking.event_date}T{booking.event_time}",
            'url': booking.get_absolute_url(),
            'className': f'booking-status-{booking.booking_status}',
            'extendedProps': {
                'booking_id': booking.id,
                'client': booking.client.username,
                'provider': booking.service_provider.username,
                'status': booking.booking_status,
            }
        })

    context = {
        'calendar_events': calendar_events,
    }

    return render(request, 'bookings/booking_calendar.html', context)