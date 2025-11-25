from django.contrib import admin
from .models import Notification


# NOTIFICATION ADMIN DECORATOR
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = ['id', 'recipient', 'notification_type', 'title_preview', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at', 'recipient']
    search_fields = ['title', 'message', 'recipient__username']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


    # TITLE PREVIEW METHOD
    def title_preview(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title

    title_preview.short_description = 'Title'
