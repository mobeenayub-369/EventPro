from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Notification


# NOTIFICATIONS LIST VIEW
@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')


    # UNREAD COUNT CALCULATION
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count
    }
    return render(request, 'notifications/notifications_list.html', context)


# MARK AS READ VIEW
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.mark_as_read()
    return redirect(notification.get_absolute_url())


# MARK ALL AS READ VIEW
@login_required
def mark_all_as_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications_list')


# GET UNREAD COUNT API
@login_required
def get_unread_count_api(request):
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).count()

    return JsonResponse({'unread_count': unread_count})


# DELETE NOTIFICATION VIEW
@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications_list')


# CLEAR ALL NOTIFICATIONS VIEW
@login_required
def clear_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect('notifications_list')
 