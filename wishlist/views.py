from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import IntegrityError

from .models import Wishlist, WishlistItem
from .forms import WishlistItemForm
from events.models import Event


# Wishlist Detail View
@login_required
def wishlist_detail(request):
    # Get or create user's wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.all().select_related('event', 'event__organizer', 'event__category')

    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist/wishlist_detail.html', context)


# Add to Wishlist View
@login_required
def add_to_wishlist(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)

    # Get or create user's wishlist
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    # Check if event is already in wishlist
    if WishlistItem.objects.filter(wishlist=wishlist, event=event).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Event is already in your wishlist.'
            })
        messages.warning(request, 'This event is already in your wishlist.')
        return redirect('event_detail', slug=event.slug)

    # Add event to wishlist
    try:
        WishlistItem.objects.create(wishlist=wishlist, event=event)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Event added to wishlist!',
                'wishlist_count': wishlist.items_count
            })

        messages.success(request, 'Event added to your wishlist!')
        return redirect('event_detail', slug=event.slug)

    except IntegrityError:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Failed to add event to wishlist.'
            })
        messages.error(request, 'Failed to add event to wishlist.')
        return redirect('event_detail', slug=event.slug)


# Remove from Wishlist View
@login_required
def remove_from_wishlist(request, item_id):
    wishlist_item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    event_slug = wishlist_item.event.slug

    # Remove item from wishlist
    wishlist_item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist = Wishlist.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'message': 'Event removed from wishlist.',
            'wishlist_count': wishlist.items_count
        })

    messages.success(request, 'Event removed from your wishlist.')

    # Redirect back to appropriate page
    referer = request.META.get('HTTP_REFERER')
    if referer and 'wishlist' in referer:
        return redirect('wishlist_detail')
    else:
        return redirect('event_detail', slug=event_slug)


# Clear Wishlist View
@login_required
def clear_wishlist(request):
    wishlist = get_object_or_404(Wishlist, user=request.user)

    if request.method == 'POST':
        items_count = wishlist.items_count
        wishlist.items.all().delete()

        messages.success(request, f'All {items_count} events removed from your wishlist.')
        return redirect('wishlist_detail')

    # Show confirmation page for GET requests
    return render(request, 'wishlist/clear_wishlist.html', {'wishlist': wishlist})


# Toggle Wishlist View (AJAX)
@login_required
def toggle_wishlist(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    # Check if event is in wishlist
    wishlist_item = WishlistItem.objects.filter(wishlist=wishlist, event=event).first()

    if wishlist_item:
        # Remove from wishlist
        wishlist_item.delete()
        action = 'removed'
        is_in_wishlist = False
    else:
        # Add to wishlist
        WishlistItem.objects.create(wishlist=wishlist, event=event)
        action = 'added'
        is_in_wishlist = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'is_in_wishlist': is_in_wishlist,
            'wishlist_count': wishlist.items_count,
            'message': f'Event {action} from wishlist!'
        })

    messages.success(request, f'Event {action} from your wishlist!')
    return redirect('event_detail', slug=event.slug)


# Wishlist Count API View
@login_required
def wishlist_count(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        return JsonResponse({
            'count': wishlist.items_count
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)