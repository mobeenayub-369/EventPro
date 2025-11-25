from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventImage


# Event Admin with Image Previews and Enhanced Features
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin interface for Event model with image previews and comprehensive management
    """
    list_display = [
        'title', 'organizer', 'category', 'date', 'location', 'price',
        'image_preview', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = ['is_active', 'is_featured', 'category', 'date', 'created_at']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'is_featured']
    date_hierarchy = 'date'
    readonly_fields = [
        'created_at', 'updated_at', 'main_image_preview',
        'thumbnail_preview', 'image_preview', 'available_seats'
    ]

    # IMAGE UPLOAD: Fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'slug', 'description', 'organizer', 'category', 'tags'
            )
        }),
        ('Event Details', {
            'fields': (
                'date', 'time', 'location', 'price', 'capacity'
            )
        }),
        ('Event Images', {
            'fields': (
                'main_image', 'main_image_preview',
                'thumbnail', 'thumbnail_preview',
                'image', 'image_preview',
                'gallery_images'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Metadata', {
            'fields': (
                'is_active', 'is_featured',
                'available_seats', 'created_at', 'updated_at'
            )
        }),
    )

    # IMAGE UPLOAD: Image preview methods
    def main_image_preview(self, obj):
        """Display main image thumbnail in admin"""
        if obj.main_image:
            return format_html(
                '<img src="{}" width="100" height="75" style="object-fit: cover; border-radius: 5px;" />',
                obj.main_image.url
            )
        return "No Main Image"

    main_image_preview.short_description = 'Main Image Preview'

    def thumbnail_preview(self, obj):
        """Display thumbnail preview in admin"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="80" height="60" style="object-fit: cover; border-radius: 5px;" />',
                obj.thumbnail.url
            )
        return "No Thumbnail"

    thumbnail_preview.short_description = 'Thumbnail Preview'

    def image_preview(self, obj):
        """Display general image preview in admin list"""
        display_image = obj.get_display_image()
        if display_image:
            return format_html(
                '<img src="{}" width="60" height="45" style="object-fit: cover; border-radius: 3px;" />',
                display_image
            )
        return "No Image"

    image_preview.short_description = 'Image'

    # Available seats method
    def available_seats(self, obj):
        return obj.available_seats()

    available_seats.short_description = 'Available Seats'

    # IMAGE UPLOAD: Method to show image count
    def image_count(self, obj):
        return obj.image_count

    image_count.short_description = 'Images'


# IMAGE UPLOAD: Admin for EventImage model
@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    """
    Admin interface for EventImage model
    """
    list_display = ['image_preview', 'caption', 'uploaded_at', 'event_count']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'events__title']
    readonly_fields = ['uploaded_at', 'image_preview_large']

    fieldsets = (
        ('Image Details', {
            'fields': ('image', 'image_preview_large', 'caption')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        """Display image thumbnail in admin list"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 3px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = 'Image'

    def image_preview_large(self, obj):
        """Display larger image preview in admin detail"""
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="max-height: 300px; object-fit: contain; border-radius: 8px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview_large.short_description = 'Image Preview'

    def event_count(self, obj):
        """Count of events using this image"""
        return obj.events.count()

    event_count.short_description = 'Used in Events'