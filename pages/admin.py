from django.contrib import admin
from .models import Page


# Page Admin Configuration
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ['title', 'slug', 'status', 'show_in_header', 'show_in_footer',
                    'order', 'created_by', 'created_at', 'is_published']

    # Filter options
    list_filter = ['status', 'show_in_header', 'show_in_footer', 'created_at']

    # Search functionality
    search_fields = ['title', 'content', 'slug']

    # Prepopulated fields
    prepopulated_fields = {'slug': ('title',)}

    # Editable in list view
    list_editable = ['status', 'order', 'show_in_header', 'show_in_footer']

    # Date-based navigation
    date_hierarchy = 'created_at'

    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'published_at']

    # Field organization in edit view
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content')
        }),
        ('SEO Settings', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Page Settings', {
            'fields': ('status', 'show_in_header', 'show_in_footer', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    # Auto-set created_by user
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)