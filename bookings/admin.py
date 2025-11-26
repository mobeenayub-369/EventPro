from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingMessage, BookingRevision


class BookingMessageInline(admin.TabularInline):
    model = BookingMessage
    extra = 0
    fields = ['sender', 'message_preview', 'attachment', 'is_read', 'created_at']
    readonly_fields = ['message_preview', 'created_at']

    def message_preview(self, obj):
        if obj.message:
            preview = obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
            return format_html('<span title="{}">{}</span>', obj.message, preview)
        return "No message"

    message_preview.short_description = 'Message'


class BookingRevisionInline(admin.TabularInline):
    model = BookingRevision
    extra = 0
    fields = ['requested_by', 'revision_details_preview', 'additional_cost', 'status', 'created_at']
    readonly_fields = ['revision_details_preview', 'created_at']

    def revision_details_preview(self, obj):
        if obj.revision_details:
            preview = obj.revision_details[:50] + '...' if len(obj.revision_details) > 50 else obj.revision_details
            return format_html('<span title="{}">{}</span>', obj.revision_details, preview)
        return "No details"

    revision_details_preview.short_description = 'Revision Details'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client', 'service_provider', 'event',
        'booking_status_badge', 'payment_status_badge',
        'event_date', 'total_amount', 'created_at'
    ]

    list_filter = [
        'booking_status', 'payment_status', 'event_date',
        'created_at', 'event__event_type'
    ]

    search_fields = [
        'id', 'client__username', 'service_provider__username',
        'event__title', 'event_location'
    ]

    list_editable = ['booking_status', 'payment_status']

    readonly_fields = [
        'created_at', 'updated_at', 'confirmed_at',
        'completed_at', 'cancelled_at', 'get_remaining_amount'
    ]

    fieldsets = (
        ('Booking Information', {
            'fields': (
                'client', 'service_provider', 'event'
            )
        }),
        ('Event Details', {
            'fields': (
                'event_date', 'event_time', 'event_duration',
                'event_location', 'number_of_guests', 'special_requirements'
            )
        }),
        ('Pricing & Payment', {
            'fields': (
                'base_price', 'additional_charges', 'discount_amount',
                'total_amount', 'amount_paid', 'get_remaining_amount'
            )
        }),
        ('Status Tracking', {
            'fields': (
                'booking_status', 'payment_status',
                'confirmed_at', 'completed_at', 'cancelled_at'
            )
        }),
        ('Notes & Communication', {
            'fields': (
                'client_notes', 'provider_notes'
            )
        }),
        ('Metadata', {
            'fields': (
                'created_at', 'updated_at'
            )
        }),
    )

    inlines = [BookingMessageInline, BookingRevisionInline]

    def booking_status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'in_progress': 'info',
            'completed': 'primary',
            'cancelled': 'secondary',
            'rejected': 'danger',
        }
        color = status_colors.get(obj.booking_status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_booking_status_display()
        )

    booking_status_badge.short_description = 'Status'

    def payment_status_badge(self, obj):
        status_colors = {
            'pending': 'warning',
            'paid': 'success',
            'failed': 'danger',
            'refunded': 'info',
            'partially_refunded': 'primary',
        }
        color = status_colors.get(obj.payment_status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_payment_status_display()
        )

    payment_status_badge.short_description = 'Payment'

    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()

    get_remaining_amount.short_description = 'Remaining Amount'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'client', 'service_provider', 'event'
        )


@admin.register(BookingMessage)
class BookingMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'sender', 'message_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['booking__id', 'sender__username', 'message']
    list_editable = ['is_read']
    readonly_fields = ['created_at']

    def message_preview(self, obj):
        if obj.message:
            return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        return "No message"

    message_preview.short_description = 'Message'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'sender')


@admin.register(BookingRevision)
class BookingRevisionAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'requested_by', 'status_badge', 'additional_cost', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['booking__id', 'requested_by__username', 'revision_details']
    list_editable = ['additional_cost']
    readonly_fields = ['created_at', 'responded_at']

    def status_badge(self, obj):
        status_colors = {
            'requested': 'warning',
            'approved': 'success',
            'rejected': 'danger',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking', 'requested_by')