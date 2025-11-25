from django.db import models
from django.contrib.auth import get_user_model
from events.models import Event

# Get the custom user model
User = get_user_model()


# Main Booking Model for event bookings
class Booking(models.Model):
    # Booking status choices
    BOOKING_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    # Payment status choices
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refund', 'Refund'),
    )

    # User and Event relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')

    # Booking identification and details
    booking_id = models.CharField(max_length=20, unique=True)
    ticket_count = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Status management
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    booking_date = models.DateTimeField()

    # Additional information
    special_requests = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    def __str__(self):
        return f"Booking {self.booking_id} - {self.user.username}"

    # Auto-generate booking ID if not provided
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BK{self.id:06d}" if self.id else "BKTEMP"
        super().save(*args, **kwargs)

    # STEP 3: FIX - Property to replace tickets_count for admin display
    @property
    def tickets_count(self):
        """Return ticket count for admin display (replaces missing tickets_count field)"""
        return self.ticket_count


# Booking Ticket Model for individual ticket types in a booking
class BookingTicket(models.Model):
    # Relationship with booking
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets')

    # Ticket details
    ticket_type = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.ticket_type} x {self.quantity}"

# STEP 4: IMPLEMENTATION - Payment model has been REMOVED from bookings app
# Payment model is now located in payments app to avoid model clash
# This resolves the Payment model conflict between bookings and payments apps