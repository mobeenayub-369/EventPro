from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    list_per_page = 50

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_messages', 'email_orders', 'push_messages']
    search_fields = ['user__username']