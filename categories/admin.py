from django.contrib import admin
from .models import Category, Tag


# Category Admin with Image Preview
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model with image preview and enhanced features
    """
    list_display = ['name', 'slug', 'image_preview', 'is_active', 'events_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

    # IMAGE UPLOAD: Fields to display in admin form
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'is_active')
        }),
        ('Category Image', {
            'fields': ('image', 'image_preview'),
            'classes': ('collapse',)  # Can be collapsed
        }),
    )

    # IMAGE UPLOAD: Readonly field for image preview
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        """
        Display image thumbnail in admin list and detail view
        """
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'
        return "No Image"

    image_preview.short_description = 'Image Preview'
    image_preview.allow_tags = True

    # Events Count Method
    def events_count(self, obj):
        return obj.event_set.count()

    events_count.short_description = 'Events'


# Tag Admin Decorator
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model
    """
    list_display = ['name', 'slug', 'events_count', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    # Fieldsets for better organization
    fieldsets = (
        ('Tag Information', {
            'fields': ('name', 'slug', 'description')
        }),
    )

    # Events Count
    def events_count(self, obj):
        return obj.event_set.count()

    events_count.short_description = 'Events'