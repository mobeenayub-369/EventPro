from django.contrib import admin
from .models import SupportTicket, TicketResponse, FAQ


# Support Ticket Admin Decorator
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'user', 'subject', 'ticket_type', 'priority',
                    'status', 'assigned_to', 'is_resolved', 'created_at']
    list_filter = ['status', 'priority', 'ticket_type', 'is_resolved', 'created_at']
    search_fields = ['ticket_id', 'subject', 'user__username', 'user__email']
    list_editable = ['status', 'priority', 'assigned_to']
    date_hierarchy = 'created_at'
    readonly_fields = ['ticket_id', 'created_at', 'updated_at', 'resolved_at']
    filter_horizontal = []

    # Fieldsets for organized display
    fieldsets = (
        ('Basic Information', {
            'fields': ('ticket_id', 'user', 'subject', 'description')
        }),
        ('Ticket Details', {
            'fields': ('ticket_type', 'priority', 'status', 'assigned_to')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolution_notes', 'resolved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Ticket Response Admin
@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'is_internal_note', 'created_at']
    list_filter = ['is_internal_note', 'created_at']
    search_fields = ['ticket__ticket_id', 'user__username', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


# FAQ Admin
@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']