from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Wishlist, WishlistItem, WishlistShare, WishlistNotification
from events.models import Event


@login_required
def wishlist_view(request):
    """User's wishlist page"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = wishlist.items.all()

    # Calculate statistics
    total_value = sum(item.event.price for item in wishlist_items if item.event.price)
    upcoming_events = wishlist_items.filter(event__date__gte=timezone.now().date())
    past_events = wishlist_items.filter(event__date__lt=timezone.now().date())

    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
        'total_value': total_value,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'items_count': wishlist.items_count,
    }
    return render(request, 'wishlist/wishlist.html', context)


@login_required
def add_to_wishlist(request, event_id):
    """Add event to wishlist (AJAX)"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id, is_active=True, is_approved=True)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Check if already in wishlist
        if WishlistItem.objects.filter(wishlist=wishlist, event=event).exists():
            return JsonResponse({
                'success': False,
                'message': 'Event is already in your wishlist.'
            })

        # Add to wishlist
        WishlistItem.objects.create(wishlist=wishlist, event=event)

        return JsonResponse({
            'success': True,
            'message': 'Event added to wishlist successfully!',
            'wishlist_count': wishlist.items_count
        })

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def remove_from_wishlist(request, event_id):
    """Remove event from wishlist (AJAX)"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        wishlist = get_object_or_404(Wishlist, user=request.user)

        try:
            wishlist_item = WishlistItem.objects.get(wishlist=wishlist, event=event)
            wishlist_item.delete()

            return JsonResponse({
                'success': True,
                'message': 'Event removed from wishlist.',
                'wishlist_count': wishlist.items_count
            })
        except WishlistItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Event not found in your wishlist.'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def toggle_wishlist(request, event_id):
    """Toggle event in wishlist (AJAX)"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id, is_active=True, is_approved=True)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        try:
            # Remove if exists
            wishlist_item = WishlistItem.objects.get(wishlist=wishlist, event=event)
            wishlist_item.delete()
            action = 'removed'
        except WishlistItem.DoesNotExist:
            # Add if not exists
            WishlistItem.objects.create(wishlist=wishlist, event=event)
            action = 'added'

        return JsonResponse({
            'success': True,
            'action': action,
            'message': f'Event {action} from wishlist.',
            'wishlist_count': wishlist.items_count,
            'in_wishlist': action == 'added'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def clear_wishlist(request):
    """Clear entire wishlist"""
    if request.method == 'POST':
        wishlist = get_object_or_404(Wishlist, user=request.user)
        items_count = wishlist.items_count
        wishlist.items.all().delete()

        messages.success(request, f'Cleared {items_count} items from your wishlist.')
        return redirect('wishlist:wishlist_view')

    return redirect('wishlist:wishlist_view')


@login_required
def share_wishlist(request):
    """Create shareable wishlist link"""
    wishlist = get_object_or_404(Wishlist, user=request.user)

    if request.method == 'POST':
        # Deactivate previous active shares
        WishlistShare.objects.filter(wishlist=wishlist, is_active=True).update(is_active=False)

        # Create new share
        share = WishlistShare.objects.create(
            wishlist=wishlist,
            created_by=request.user
        )

        share_url = request.build_absolute_uri(
            f'/wishlist/shared/{share.share_token}/'
        )

        return JsonResponse({
            'success': True,
            'share_url': share_url,
            'expires_at': share.expires_at.strftime('%b %d, %Y %H:%M')
        })

    # Get active shares
    active_shares = WishlistShare.objects.filter(
        wishlist=wishlist,
        is_active=True,
        expires_at__gt=timezone.now()
    )

    context = {
        'wishlist': wishlist,
        'active_shares': active_shares,
    }
    return render(request, 'wishlist/share_wishlist.html', context)


def shared_wishlist(request, share_token):
    """View shared wishlist"""
    share = get_object_or_404(
        WishlistShare,
        share_token=share_token,
        is_active=True,
        expires_at__gt=timezone.now()
    )

    wishlist = share.wishlist
    wishlist_items = wishlist.items.all()

    context = {
        'share': share,
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
        'is_owner': request.user == wishlist.user,
    }
    return render(request, 'wishlist/shared_wishlist.html', context)


@login_required
def wishlist_notifications(request):
    """User's wishlist notifications"""
    notifications = WishlistNotification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Mark as read when viewing
    unread_notifications = notifications.filter(is_read=False)
    unread_notifications.update(is_read=True)

    context = {
        'notifications': notifications,
    }
    return render(request, 'wishlist/notifications.html', context)


# Utility functions
def check_wishlist_notifications():
    """Check and create wishlist notifications (run as cron job)"""
    # This would be called periodically to check for:
    # - Price drops
    # - Events becoming available
    # - Event reminders
    # - Almost full events
    pass


@login_required
def get_wishlist_count(request):
    """Get wishlist items count for navbar (AJAX)"""
    try:
        wishlist = Wishlist.objects.get(user=request.user)
        count = wishlist.items_count
    except Wishlist.DoesNotExist:
        count = 0

    return JsonResponse({'count': count})