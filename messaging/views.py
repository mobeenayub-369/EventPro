from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from .models import MessageThread, Message
from .forms import MessageForm
from django.contrib.auth import get_user_model

# User Model Setup
User= get_user_model()

@login_required
def inbox(request):
    threads= MessageThread.objects.filter(
        participants= request.user
    ).prefetch_related('participants', 'messages').order_by('-updated_at')


    # Context Data (send thread data to template)
    context= {
        'threads': threads
    }

    return render(request, 'messaging/inbox.html', context)


# Thread Detail View
@login_required
def thread_detail(request, thread_id):
    thread= get_object_or_404(
        MessageThread,
        id= thread_id,
        participants= request.user
    )

    # Messages Fetch
    message_list= thread.messages.select_related('sender').all()
    unread_messages= message_list.filter(is_read= False).exclude(sender= request.user)
    unread_messages.updated(is_read= True)


    # Message Form
    form= MessageForm()
    other_participant= thread.get_other_participant(request.user)


    # Form Submit Handle
    if request.method == 'POST':
        form= MessageForm(request.POST)
        if form.is_valid():
            message= form.save(commit= False)
            message.thread= thread
            message.sender= request.user
            message.save()
            return redirect('thread_detail', thread_id= thread.id)


    context= {
        'thread': thread,
        'message_list': message_list,
        'form': form,
        'other_participant': other_participant
    }

    return render(request, 'messaging/thread_detail.html', context)


# Start Thread View
@login_required
def start_thread(request, user_id):
    other_user= get_object_or_404(User, id= user_id)

    # Existing Thread Check
    existing_thread= MessageThread.objects.filter(
        participants= request.user
    ).filter(participants= other_user).first()

    # Existing Thread Redirect
    if existing_thread:
        return redirect('thread_detail', thread_id= existing_thread.id)

    # New Thread Create
    new_thread= MessageThread.objects.create()
    new_thread.participants.add(request_user, other_user)

    return redirect('thread_detail', thread_id= new_thread.id)


# Send Message API view
@login_required
def send_message_api(request, thread_id):
    thread= get_object_or_404(
        MessageThread,
        id= thread_id,
        participants=request.user
    )


    # Message Send Handle
    if request.method == 'POST':
        form= MessageForm(request.POST)
        if form.is_valid():
            message= form.save(commit= False)
            message.thread= thread
            message.sender= request.user
            message.save()
            return JsonResponse({'success': True, 'message_id': message.id})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success':False, 'error': 'Invalid request'})


# Get Unread Count API
@login_required
def get_unread_count(request):
    unread_count= Message.objects,filter(
        thread_participants= request.user,
        is_read= False
    ).exclude(sender= request.user).count()

    return JsonResponse({'unread_count': unread_count})