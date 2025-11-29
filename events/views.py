from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, EventImage, EventReview
from .forms import EventForm  # Aap ke existing form ka use karenge


def event_list(request):
    category = request.GET.get('category', '')

    # Active events filter karein
    events = Event.objects.filter(status='active')

    # Category filter
    if category:
        events = events.filter(event_type=category)

    context = {
        'events': events,
        'category': category,
    }

    return render(request, 'events/event_list.html', context)


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, status='active')

    # Increment view count
    event.increment_views()

    context = {
        'event': event,
    }

    return render(request, 'events/event_detail.html', context)


@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()

    return render(request, 'events/create_event.html', {'form': form})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('my_events')

    return render(request, 'events/delete_event.html', {'event': event})


@login_required
def my_events(request):
    events = Event.objects.filter(organizer=request.user)
    return render(request, 'events/my_events.html', {'events': events})