from django.contrib import admin
from .models import Wishlist, WishlistItem, WishlistShare, WishlistNotification

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['wishlist', 'event', 'added_at']
    list_filter = ['added_at', 'wishlist__user']
    search_fields = ['event__title', 'wishlist__user__username']
    readonly_fields = ['added_at']

@admin.register(WishlistShare)
class WishlistShareAdmin(admin.ModelAdmin):
    list_display = ['wishlist', 'share_token', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'created_at', 'expires_at']
    search_fields = ['wishlist__user__username', 'share_token']
    readonly_fields = ['share_token', 'created_at']

@admin.register(WishlistNotification)
class WishlistNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'event__title']
    readonly_fields = ['created_at']
    list_editable = ['is_read']