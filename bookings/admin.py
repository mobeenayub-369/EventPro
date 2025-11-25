from django.contrib import admin
from .models import Booking, BookingTicket


# STEP 5: IMPLEMENTATION - PaymentAdmin has been REMOVED from bookings app
# PaymentAdmin is now located in payments app

# Booking Admin Configuration
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # Fields to display in admin list view
    list_display = ['booking_id', 'user', 'event', 'tickets_count', 'total_amount',
                    'booking_status', 'payment_status', 'created_at']

    # STEP 6: FIX - Changed 'event_category' to 'event__category' for proper filtering
    # This allows filtering by event's category through the relationship
    list_filter = ['booking_status', 'payment_status', 'created_at', 'event__category']

    # STEP 7: FIX - Corrected field names with proper relationship syntax
    # Using double underscore for related field lookups
    search_fields = ['booking_id', 'user__username', 'event__title']

    # Fields that can be edited directly from list view
    list_editable = ['booking_status', 'payment_status']

    # Date-based navigation
    date_hierarchy = 'created_at'

    # Fields that cannot be edited
    readonly_fields = ['booking_id', 'created_at', 'updated_at']

    # Organized field groups in admin form
    fieldsets = (
        ('Basic Information', {
            'fields': ('booking_id', 'user', 'event', 'booking_date')
        }),
        ('Booking Details', {
            'fields': ('ticket_count', 'total_amount', 'special_requests')
        }),
        ('Status Information', {
            'fields': ('booking_status', 'payment_status', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )


# Booking Ticket Admin Configuration
@admin.register(BookingTicket)
class BookingTicketAdmin(admin.ModelAdmin):
    # Fields to display in admin list view
    list_display = ['booking', 'ticket_type', 'quantity', 'price', 'total_price']

    # Filter options
    list_filter = ['ticket_type']

    # Searchable fields
    search_fields = ['booking__booking_id', 'ticket_type']

    # Custom method to calculate total price
    def total_price(self, obj):
        """Calculate total price for ticket type (quantity * price)"""
        return obj.quantity * obj.price

    total_price.short_description = 'Total Price'

# STEP 8: IMPLEMENTATION - Payment model admin removed to avoid conflict
# Payment admin is now handled in payments app