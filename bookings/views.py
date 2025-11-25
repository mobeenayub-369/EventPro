from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking, BookingTicket
from .forms import BookingForm, TicketBookingForm
from events.models import Event


# Create Booking View
@login_required
def create_booking(request, event_id):
    event= get_object_or_404(Event, id= event_id)

# POST Request Handle
    if request.method == 'POST':
        form= BookingForm(request.POST)
        if form.is_valid():
            booking= form.save(commit= False)
            booking.user= request.user
            booking.event= event
            booking.total_amount= event_price * booking.tickets_count
            booking.save()

            messages.success(request, 'Booking created successfully! Proceed to payment.')
            return redirect('booking_payment', booking_id= booking.id)


# GET Request Handle
    else:
        form= BookingForm()

    return render(request, 'bookings/create_booking.html', {
        'form': form,
        'event': event
    })


# My Bookings View
@login_required
def my_bookings(request):
    bookings= Booking.objects.filter(user= request.user).order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


# Booking Detail View
@login_required
def booking_detail(request, booking_id):
    booking= get_object_or_404(Booking, id= booking_id, user= request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


# Booking Payment View
@login_required
def booking_payment(request, booking_id):
    booking= get_object_or_404(Booking, id= booking_id, user= request.user)

# Payment Processing Logic
    if request.method == 'POST':
        booking.payment_status= 'paid'
        booking.booking_status= 'confirmed'
        booking.save()

        # Create payment record
        Payment.objects.create(
            booking= booking,
            payment_id= f"Pay{booking.id:06d}",
            payment_method= 'card',
            amount= booking.total_amount
        )

        messages.success(request, 'Payment successful! Your booking is confirmed.')
        return redirect('booking_detail', booking_id= booking.id)

    return render(request, 'bookings/booking_payment.html', {'booking': booking})


# Cancel Booking View
@login_required
def cancel_booking(request, booking_id):
    booking= get_object_or_404(Booking, id= booking_id, user= request.user)

    if request.method == 'POST':
        reason= request.POST.get('cancellation_reason','')
        booking.booking_status= 'cancelled'
        booking.cancellation_reason= reason
        booking.save()

        messages.success(request, 'Booking cancelled successfully.')
        return redirect('my_bookings')

    return render(request, 'bookings/cancel_booking.html', {'booking': booking})


# Booking Invoice View
@login_required
def booking_invoice(request, booking_id):
    booking= get_object_or_404(Booking, id= booking_id, user= request.user)
    return render(request, 'bookings/booking_invoice.html', {'booking': booking})