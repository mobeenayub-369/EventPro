from django.contrib import admin
from .models import Booking, BookingMessage, BookingRevision


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'client',
        'service_provider',
        'event',  # ← Actual field
        'booking_status',
        'payment_status',
        'total_amount',
        'created_at'
    ]
    list_filter = [
        'booking_status',
        'payment_status',
        'created_at'
    ]
    search_fields = [
        'client__username',
        'service_provider__username',
        'event__title'
    ]
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['booking_status', 'payment_status']
    list_per_page = 20


@admin.register(BookingMessage)
class BookingMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'sender', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['booking__id', 'sender__username', 'content']

    def content_preview(self, obj):
        if obj.content:
            return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return "No content"

    content_preview.short_description = 'Message'


@admin.register(BookingRevision)
class BookingRevisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'requested_by', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking__id', 'requested_by__username']