from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for Category model.
    Defines how categories are displayed and managed in Django admin.
    """

    # Fields to display in the admin list view
    list_display = ['name', 'slug', 'is_active', 'created_at']

    # Filters for easy navigation in admin
    list_filter = ['is_active', 'created_at']

    # Searchable fields in admin
    search_fields = ['name', 'description']

    # Fields that should be automatically populated from other fields
    prepopulated_fields = {'slug': ('name',)}

    # Fields that can be edited directly from the list view
    list_editable = ['is_active']