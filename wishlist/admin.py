from django.contrib import admin
from .models import Wishlist, WishlistItem


# Wishlist Admin Decorator
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    # Items count method for admin
    def items_count(self, obj):
        return obj.items_count

    items_count.short_description = 'Items Count'

    # Total price method for admin
    def total_price(self, obj):
        return f"Rs. {obj.total_price}"

    total_price.short_description = 'Total Price'


# Wishlist Item Admin
@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['event', 'wishlist', 'added_at']
    list_filter = ['added_at', 'wishlist__user']
    search_fields = ['event__title', 'wishlist__user__username']
    readonly_fields = ['added_at']
    date_hierarchy = 'added_at'

    # Fieldsets for organized display
    fieldsets = (
        ('Basic Information', {
            'fields': ('wishlist', 'event')
        }),
        ('Timestamps', {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )