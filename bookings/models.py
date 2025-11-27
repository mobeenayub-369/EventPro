from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    # Basic Information
    client = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='bookings_as_client'
    )
    service_provider = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='bookings_as_provider'
    )
    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    # Booking Details
    booking_date = models.DateTimeField(auto_now_add=True)
    # event_date = models.DateField(help_text="Date when the event will take place")
    event_time = models.TimeField(help_text="Time when the event will start")
    event_duration = models.PositiveIntegerField(
        default=4,
        help_text="Duration of the event in hours",
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    # event_location = models.CharField(
    #     max_length=255,
    #     help_text="Full address or venue of the event"
    # )
    number_of_guests = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(1)],
        help_text="Estimated number of attendees"
    )

    # Special Requirements
    special_requirements = models.TextField(
        blank=True,
        help_text="Any special requests or requirements for the event"
    )

    # Pricing & Payment
    # base_price = models.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     help_text="Original price of the service"
    # )
    additional_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Any additional charges (transportation, equipment, etc.)"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Any discounts applied"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final amount to be paid"
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Amount that has been paid so far"
    )

    # Status Tracking
    booking_status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        default='pending'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    # Dates & Metadata
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Communication
    client_notes = models.TextField(blank=True, help_text="Notes from the client")
    provider_notes = models.TextField(blank=True, help_text="Notes from the service provider")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        indexes = [
            models.Index(fields=['client', 'booking_status']),
            models.Index(fields=['service_provider', 'booking_status']),
            # models.Index(fields=['event_date', 'booking_status']),
        ]

    def __str__(self):
        return f"Booking #{self.id} - {self.event.title} - {self.client.username}"

    # def save(self, *args, **kwargs):
    #     # Calculate total amount before saving
    #     self.total_amount = self.base_price + self.additional_charges - self.discount_amount
    #     super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('bookings:booking_detail', kwargs={'pk': self.pk})

    def get_remaining_amount(self):
        return self.total_amount - self.amount_paid

    def is_fully_paid(self):
        return self.amount_paid >= self.total_amount

    def can_be_cancelled(self):
        return self.booking_status in ['pending', 'confirmed']

    def get_timeline_status(self):
        """Get current status in timeline format"""
        timeline = []

        if self.created_at:
            timeline.append({
                'status': 'created',
                'title': 'Booking Request Sent',
                'description': 'Your booking request has been submitted',
                'date': self.created_at,
                'completed': True
            })

        if self.confirmed_at:
            timeline.append({
                'status': 'confirmed',
                'title': 'Booking Confirmed',
                'description': 'Service provider has confirmed your booking',
                'date': self.confirmed_at,
                'completed': True
            })

        if self.booking_status == 'in_progress':
            timeline.append({
                'status': 'in_progress',
                'title': 'Event in Progress',
                'description': 'Your event is currently happening',
                'date': timezone.now(),
                'completed': False
            })

        if self.completed_at:
            timeline.append({
                'status': 'completed',
                'title': 'Event Completed',
                'description': 'Your event has been successfully completed',
                'date': self.completed_at,
                'completed': True
            })

        if self.cancelled_at:
            timeline.append({
                'status': 'cancelled',
                'title': 'Booking Cancelled',
                'description': 'This booking has been cancelled',
                'date': self.cancelled_at,
                'completed': True
            })

        return timeline


class BookingMessage(models.Model):
    """
    Messages between client and service provider for a specific booking
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE,
        related_name='booking_messages'
    )
    message = models.TextField()
    attachment = models.FileField(
        upload_to='booking_attachments/%Y/%m/%d/',
        blank=True,
        null=True
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Booking Message'
        verbose_name_plural = 'Booking Messages'

    def __str__(self):
        return f"Message #{self.id} - Booking #{self.booking.id}"


class BookingRevision(models.Model):
    """
    Track revisions or changes to a booking
    """
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='revisions'
    )
    requested_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.CASCADE
    )
    revision_details = models.TextField(help_text="Details of the requested changes")
    additional_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('requested', 'Requested'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='requested'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking Revision'
        verbose_name_plural = 'Booking Revisions'

    def __str__(self):
        return f"Revision #{self.id} - Booking #{self.booking.id}"