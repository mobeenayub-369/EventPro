from django.contrib import admin
from .models import Page, FAQ, ContactSubmission

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'page_type', 'is_active', 'order', 'created_at']
    list_filter = ['page_type', 'is_active', 'show_in_footer', 'show_in_navigation']
    search_fields = ['title', 'content', 'slug']
    list_editable = ['is_active', 'order']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at', 'ip_address', 'user_agent']
    list_editable = ['status']