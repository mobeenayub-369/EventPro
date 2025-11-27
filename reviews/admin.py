from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'event',  # ← Actual field
        'user',  # ← Actual field
        'rating',  # ← Actual field
        'content_preview',
        'created_at'
    ]
    list_filter = [
        'rating',
        'created_at'
    ]
    search_fields = [
        'content',
        'user__username',
        'event__title'
    ]
    readonly_fields = ['created_at']
    list_per_page = 20

    def content_preview(self, obj):
        if obj.content:
            return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
        return "No content"

    content_preview.short_description = 'Review Content'