from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Max
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Conversation, Message, UserMessageSettings, BlockedUser
from .forms import MessageForm, NewConversationForm, UserMessageSettingsForm, SearchMessagesForm


@login_required
def inbox(request):
    """
    Display user's inbox with all conversations.
    Similar to Fiverr's inbox with conversation threads.
    """
    # Get all conversations for the user
    conversations = Conversation.objects.filter(participants=request.user)

    # Apply filters
    show_archived = request.GET.get('show_archived') == 'true'
    show_unread = request.GET.get('show_unread') == 'true'

    if not show_archived:
        conversations = conversations.filter(is_archived=False)

    if show_unread:
        conversations = conversations.annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
        ).filter(unread_count__gt=0)

    # Get conversation statistics
    inbox_stats = {
        'total_conversations': conversations.count(),
        'unread_conversations': conversations.annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user))
        ).filter(unread_count__gt=0).count(),
        'archived_conversations': Conversation.objects.filter(
            participants=request.user,
            is_archived=True
        ).count(),
    }

    # Search functionality
    search_form = SearchMessagesForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        has_attachments = search_form.cleaned_data.get('has_attachments')

        if query:
            conversations = conversations.filter(
                Q(messages__content__icontains=query) |
                Q(subject__icontains=query) |
                Q(participants__username__icontains=query)
            ).distinct()

        if date_from:
            conversations = conversations.filter(messages__timestamp__date__gte=date_from)

        if date_to:
            conversations = conversations.filter(messages__timestamp__date__lte=date_to)

        if has_attachments:
            conversations = conversations.filter(messages__attachment__isnull=False).distinct()

    # Order by last message timestamp
    conversations = conversations.annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    context = {
        'conversations': conversations,
        'inbox_stats': inbox_stats,
        'search_form': search_form,
        'show_archived': show_archived,
        'show_unread': show_unread,
        'title': 'Messages - EventPro'
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def thread_detail(request, conversation_id):
    """
    Display a specific conversation thread with messages.
    Similar to Fiverr's conversation view.
    """
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    # Mark messages as read when viewing conversation
    conversation.mark_as_read(request.user)

    # Get messages with pagination
    message_list = conversation.messages.all().order_by('timestamp')
    paginator = Paginator(message_list, 50)  # 50 messages per page
    page_number = request.GET.get('page')
    messages_page = paginator.get_page(page_number)

    # Message form for replying
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if user is blocked
            other_participant = conversation.get_other_participant(request.user)
            if BlockedUser.objects.filter(user=other_participant, blocked_user=request.user).exists():
                messages.error(request, 'You cannot send messages to this user. You have been blocked.')
                return redirect('messaging:thread_detail', conversation_id=conversation.id)

            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            messages.success(request, 'Message sent successfully!')
            return redirect('messaging:thread_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'messages': messages_page,
        'form': form,
        'other_user': conversation.get_other_participant(request.user),
        'title': f'Conversation with {conversation.get_other_participant(request.user).username}'
    }
    return render(request, 'messaging/thread_detail.html', context)


@login_required
def new_conversation(request, user_id=None):
    """
    Start a new conversation with another user.
    """
    recipient = None
    if user_id:
        recipient = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = NewConversationForm(request.POST, sender=request.user)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message_content = form.cleaned_data['message']

            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=recipient
            ).first()

            if existing_conversation:
                conversation = existing_conversation
                if subject and not conversation.subject:
                    conversation.subject = subject
                    conversation.save()
            else:
                # Create new conversation
                conversation = Conversation.objects.create(subject=subject)
                conversation.participants.add(request.user, recipient)

            # Create first message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_content
            )

            messages.success(request, f'Message sent to {recipient.username}!')
            return redirect('messaging:thread_detail', conversation_id=conversation.id)
    else:
        initial = {}
        if recipient:
            initial['recipient'] = recipient

        form = NewConversationForm(initial=initial, sender=request.user)

    context = {
        'form': form,
        'recipient': recipient,
        'title': 'New Message - EventPro'
    }
    return render(request, 'messaging/new_conversation.html', context)


@login_required
def archive_conversation(request, conversation_id):
    """
    Archive or unarchive a conversation.
    """
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    if request.method == 'POST':
        conversation.is_archived = not conversation.is_archived
        conversation.save()

        action = "archived" if conversation.is_archived else "unarchived"
        messages.success(request, f'Conversation {action} successfully!')

    return redirect('messaging:inbox')


@login_required
def delete_conversation(request, conversation_id):
    """
    Delete a conversation (soft delete for user).
    """
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        participants=request.user
    )

    if request.method == 'POST':
        # Remove user from conversation participants
        conversation.participants.remove(request.user)

        # If no participants left, delete the conversation
        if conversation.participants.count() == 0:
            conversation.delete()

        messages.success(request, 'Conversation deleted successfully!')
        return redirect('messaging:inbox')

    context = {
        'conversation': conversation,
        'title': 'Delete Conversation - EventPro'
    }
    return render(request, 'messaging/delete_conversation.html', context)


@login_required
def message_settings(request):
    """
    User messaging settings and preferences.
    """
    settings_instance, created = UserMessageSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserMessageSettingsForm(request.POST, instance=settings_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Message settings updated successfully!')
            return redirect('messaging:message_settings')
    else:
        form = UserMessageSettingsForm(instance=settings_instance)

    # Get blocked users
    blocked_users = BlockedUser.objects.filter(user=request.user).select_related('blocked_user')

    context = {
        'form': form,
        'blocked_users': blocked_users,
        'title': 'Message Settings - EventPro'
    }
    return render(request, 'messaging/message_settings.html', context)


@login_required
def block_user(request, user_id):
    """
    Block a user from sending messages.
    """
    user_to_block = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Check if already blocked
        if not BlockedUser.objects.filter(user=request.user, blocked_user=user_to_block).exists():
            BlockedUser.objects.create(
                user=request.user,
                blocked_user=user_to_block,
                reason=request.POST.get('reason', '')
            )
            messages.success(request, f'{user_to_block.username} has been blocked.')
        else:
            messages.warning(request, f'{user_to_block.username} is already blocked.')

    return redirect('messaging:message_settings')


@login_required
def unblock_user(request, user_id):
    """
    Unblock a previously blocked user.
    """
    user_to_unblock = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        blocked_entry = BlockedUser.objects.filter(
            user=request.user,
            blocked_user=user_to_unblock
        ).first()

        if blocked_entry:
            blocked_entry.delete()
            messages.success(request, f'{user_to_unblock.username} has been unblocked.')
        else:
            messages.warning(request, f'{user_to_unblock.username} is not blocked.')

    return redirect('messaging:message_settings')


@login_required
def search_messages(request):
    """
    Advanced message search across all conversations.
    """
    form = SearchMessagesForm(request.GET)
    results = []

    if form.is_valid() and any(form.cleaned_data.values()):
        query = form.cleaned_data.get('query')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        has_attachments = form.cleaned_data.get('has_attachments')

        # Start with user's messages
        messages_qs = Message.objects.filter(conversation__participants=request.user)

        if query:
            messages_qs = messages_qs.filter(content__icontains=query)

        if date_from:
            messages_qs = messages_qs.filter(timestamp__date__gte=date_from)

        if date_to:
            messages_qs = messages_qs.filter(timestamp__date__lte=date_to)

        if has_attachments:
            messages_qs = messages_qs.filter(attachment__isnull=False)

        results = messages_qs.select_related('conversation', 'sender').order_by('-timestamp')

    context = {
        'form': form,
        'results': results,
        'title': 'Search Messages - EventPro'
    }
    return render(request, 'messaging/search_messages.html', context)


# AJAX views for real-time functionality
@login_required
def get_unread_count(request):
    """
    AJAX view to get unread message count for notifications.
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        unread_count = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).count()

        return JsonResponse({'unread_count': unread_count})

    return JsonResponse({'error': 'Invalid request'})


@login_required
def mark_as_read(request, message_id):
    """
    AJAX view to mark a message as read.
    """
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        message = get_object_or_404(
            Message,
            id=message_id,
            conversation__participants=request.user
        )

        if not message.is_read and message.sender != request.user:
            message.is_read = True
            message.save()

            return JsonResponse({'success': True})

    return JsonResponse({'success': False})