from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventImage, EventReview


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'display_order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="75" style="object-fit: cover;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Preview'


class EventReviewInline(admin.TabularInline):
    model = EventReview
    extra = 0
    fields = ['user', 'rating', 'comment', 'created_at', 'is_approved']
    readonly_fields = ['created_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'organizer', 'event_type', 'price',
        'capacity', 'status', 'view_count', 'booking_count',
        'average_rating', 'created_at', 'is_featured'
    ]

    list_filter = [
        'event_type', 'status', 'is_featured', 'created_at', 'updated_at'
    ]

    search_fields = [
        'title', 'description', 'organizer__username', 'organizer__email'
    ]

    list_editable = ['status', 'is_featured']

    readonly_fields = [
        'view_count', 'booking_count', 'average_rating',
        'review_count', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'description', 'organizer', 'event_type'
            )
        }),
        ('Pricing & Details', {
            'fields': (
                'price', 'currency', 'capacity', 'duration', 'location'
            )
        }),
        ('Status & Metadata', {
            'fields': (
                'status', 'is_featured',
                'view_count', 'booking_count',
                'average_rating', 'review_count',
                'created_at', 'updated_at'
            )
        }),
    )

    inlines = [EventImageInline, EventReviewInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organizer')


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ['event', 'image_preview', 'is_primary', 'display_order', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['event__title', 'caption']
    list_editable = ['is_primary', 'display_order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="75" style="object-fit: cover;" />', obj.image.url)
        return "No Image"

    image_preview.short_description = 'Image Preview'


@admin.register(EventReview)
class EventReviewAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'rating', 'comment_preview', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['event__title', 'user__username', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']

    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return "No comment"

    comment_preview.short_description = 'Comment Preview'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event', 'user')


# Admin site customization
admin.site.site_header = 'EventPro Administration'
admin.site.site_title = 'EventPro Admin'
admin.site.index_title = 'Event Management System'