from django.contrib import admin
from .models import SupportCategory, SupportTicket, TicketResponse, FAQ, KnowledgeBaseArticle

@admin.register(SupportCategory)
class SupportCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'user', 'category', 'subject', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at']
    search_fields = ['ticket_id', 'subject', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'priority']

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ['ticket', 'user', 'created_at', 'is_internal_note']
    list_filter = ['is_internal_note', 'created_at']
    search_fields = ['ticket__ticket_id', 'user__username']
    readonly_fields = ['created_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'views']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']

@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'views', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['is_published']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']