from django.contrib import admin
from .models import MessageThread, Message

# Message Inline
class MessageInline(admin.TabularInline):
    model= Message
    extra= 0
    readonly_fields = ['created_at']
    fields = ['sender', 'content', 'is_read', 'created_at']


# Message Thread Admin
@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'participants_list', 'message_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    inlines= [MessageInline]


    # Participants List
    def participants_list(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    participants_list.short_description= 'Participants'


    # Message Count
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description= 'Messages'


# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'thread', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'thread']
    search_fields = ['content', 'sender_username']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description= 'Content'