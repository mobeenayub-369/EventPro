from django.contrib import admin
from .models import Conversation, Message, UserMessageSettings, BlockedUser

# Message Inline
class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['timestamp']
    fields = ['sender', 'content', 'is_read', 'timestamp']
    show_change_link = True


# Conversation Admin
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'subject',
        'participants_list',
        'message_count',
        'is_archived',
        'created_at'
    ]
    list_filter = [
        'created_at',
        'updated_at',
        'is_archived',
        'is_blocked'
        # 'related_event'  # ← Temporarily comment out
    ]
    list_editable = ['is_archived']
    inlines = [MessageInline]
    search_fields = [
        'subject',
        'participants__username'
    ]

    def participants_list(self, obj):
        return ", ".join([user.username for user in obj.participants.all()[:3]])
    participants_list.short_description = 'Participants'

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'


# Message Admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'sender',
        'conversation_preview',
        'content_preview',
        'is_read',
        'has_attachment',
        'timestamp'
    ]
    list_filter = [
        'is_read',
        'timestamp',
        'conversation'
    ]
    search_fields = [
        'content',
        'sender__username'
    ]
    readonly_fields = ['timestamp']

    def conversation_preview(self, obj):
        return f"{obj.conversation.subject} (ID: {obj.conversation.id})"
    conversation_preview.short_description = 'Conversation'

    def content_preview(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    content_preview.short_description = 'Message'

    def has_attachment(self, obj):
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = 'Attachment'


# UserMessageSettings Admin
@admin.register(UserMessageSettings)
class UserMessageSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'email_notifications',
        'push_notifications',
        'allow_messages_from',
        'auto_responder_enabled'
    ]
    list_filter = [
        'email_notifications',
        'push_notifications',
        'allow_messages_from'
    ]
    search_fields = ['user__username']


# BlockedUser Admin
@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'blocked_user',
        'created_at'
    ]
    list_filter = ['created_at']
    search_fields = [
        'user__username',
        'blocked_user__username'
    ]