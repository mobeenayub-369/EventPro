from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Conversation(models.Model):
    """
    Conversation model for messaging between users.
    Similar to Fiverr's messaging system between buyers and sellers.
    """

    # Conversation participants
    participants = models.ManyToManyField(User, related_name='conversations')

    # Conversation metadata
    subject = models.CharField(max_length=200, blank=True, verbose_name="Conversation Subject")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Conversation settings
    is_archived = models.BooleanField(default=False, verbose_name="Archived")
    is_blocked = models.BooleanField(default=False, verbose_name="Blocked")

    # Related event (if conversation is about a specific event)
    # related_event = models.ForeignKey(
    #     'events.Event',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
        # related_name='conversations'
    # )

    class Meta:
        app_label = 'messaging'
        ordering = ['-updated_at']
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self):
        participant_names = ", ".join([user.username for user in self.participants.all()])
        return f"Conversation: {participant_names}"

    def get_absolute_url(self):
        return reverse('messaging:thread_detail', kwargs={'conversation_id': self.id})

    def get_other_participant(self, current_user):
        """Get the other participant in the conversation."""
        return self.participants.exclude(id=current_user.id).first()

    def get_unread_count(self, user):
        """Get count of unread messages for a user."""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def get_last_message(self):
        """Get the last message in the conversation."""
        return self.messages.order_by('-timestamp').first()

    def mark_as_read(self, user):
        """Mark all messages as read for a user."""
        self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)


class Message(models.Model):
    """
    Message model for individual messages in conversations.
    Supports text messages and file attachments.
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    # Message content
    content = models.TextField(verbose_name="Message")
    timestamp = models.DateTimeField(auto_now_add=True)

    # Message status
    is_read = models.BooleanField(default=False, verbose_name="Read")
    is_delivered = models.BooleanField(default=True, verbose_name="Delivered")

    # File attachment
    attachment = models.FileField(
        upload_to='message_attachments/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="Attachment"
    )
    attachment_name = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"

    def save(self, *args, **kwargs):
        # Set attachment name if file is uploaded
        if self.attachment and not self.attachment_name:
            self.attachment_name = self.attachment.name
        super().save(*args, **kwargs)

        # Update conversation's updated_at timestamp
        self.conversation.updated_at = timezone.now()
        self.conversation.save()


class UserMessageSettings(models.Model):
    """
    User-specific messaging settings and preferences.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='message_settings'
    )

    # Notification settings
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="Email Notifications"
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name="Push Notifications"
    )

    # Privacy settings
    allow_messages_from = models.CharField(
        max_length=20,
        choices=[
            ('everyone', 'Everyone'),
            ('verified', 'Verified Users Only'),
            ('none', 'No One'),
        ],
        default='everyone',
        verbose_name="Who can message you?"
    )

    # Auto-response settings
    auto_responder_enabled = models.BooleanField(
        default=False,
        verbose_name="Enable Auto-Responder"
    )
    auto_responder_message = models.TextField(
        blank=True,
        verbose_name="Auto-Response Message"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Message Settings"
        verbose_name_plural = "User Message Settings"

    def __str__(self):
        return f"Message settings for {self.user.username}"


class BlockedUser(models.Model):
    """
    Track blocked users to prevent messaging.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_users'
    )
    blocked_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocked_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, verbose_name="Block Reason")

    class Meta:
        unique_together = ['user', 'blocked_user']
        verbose_name = "Blocked User"
        verbose_name_plural = "Blocked Users"

    def __str__(self):
        return f"{self.user.username} blocked {self.blocked_user.username}"