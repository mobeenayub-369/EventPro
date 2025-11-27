from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Notification, NotificationPreference
from .forms import NotificationPreferenceForm
from .utils import create_notification, send_email_notification, send_push_notification


@login_required
def notifications_dashboard(request):
    """
    Fiverr-style notifications dashboard with filters and categories
    """
    # Get filter parameters
    notification_type = request.GET.get('type', 'all')
    read_status = request.GET.get('read', 'all')
    time_filter = request.GET.get('time', 'all')

    # Base queryset
    notifications = Notification.objects.filter(user=request.user)

    # Apply filters
    if notification_type != 'all':
        notifications = notifications.filter(notification_type=notification_type)

    if read_status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif read_status == 'read':
        notifications = notifications.filter(is_read=True)

    # Time filters
    if time_filter == 'today':
        today = timezone.now().date()
        notifications = notifications.filter(created_at__date=today)
    elif time_filter == 'week':
        week_ago = timezone.now() - timezone.timedelta(days=7)
        notifications = notifications.filter(created_at__gte=week_ago)
    elif time_filter == 'month':
        month_ago = timezone.now() - timezone.timedelta(days=30)
        notifications = notifications.filter(created_at__gte=month_ago)

    # Order by creation date (newest first)
    notifications = notifications.order_by('-created_at')

    # Pagination (Fiverr style - 15 per page)
    paginator = Paginator(notifications, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics for dashboard
    total_notifications = Notification.objects.filter(user=request.user).count()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    today_count = Notification.objects.filter(
        user=request.user,
        created_at__date=timezone.now().date()
    ).count()

    # Notification type counts
    type_counts = {}
    for notification_type, _ in Notification.NOTIFICATION_TYPES:
        type_counts[notification_type] = Notification.objects.filter(
            user=request.user,
            notification_type=notification_type
        ).count()

    context = {
        'notifications': page_obj,
        'unread_count': unread_count,
        'total_notifications': total_notifications,
        'today_count': today_count,
        'type_counts': type_counts,
        'current_filters': {
            'type': notification_type,
            'read': read_status,
            'time': time_filter,
        },
        'notification_types': Notification.NOTIFICATION_TYPES,
    }

    return render(request, 'notifications/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """
    Mark a single notification as read (AJAX)
    """
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': 'Notification marked as read',
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """
    Mark all notifications as read (AJAX)
    """
    try:
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)

        return JsonResponse({
            'success': True,
            'message': f'Marked {updated_count} notifications as read',
            'unread_count': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def mark_as_unread(request, notification_id):
    """
    Mark a notification as unread (AJAX)
    """
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = False
        notification.save()

        return JsonResponse({
            'success': True,
            'message': 'Notification marked as unread',
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """
    Delete a single notification (AJAX)
    """
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()

        return JsonResponse({
            'success': True,
            'message': 'Notification deleted successfully',
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def delete_all_read(request):
    """
    Delete all read notifications (AJAX)
    """
    try:
        deleted_count, _ = Notification.objects.filter(
            user=request.user,
            is_read=True
        ).delete()

        return JsonResponse({
            'success': True,
            'message': f'Deleted {deleted_count} read notifications',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def notification_preferences(request):
    """
    Fiverr-style notification preferences with categories
    """
    preference, created = NotificationPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your notification preferences have been updated successfully!')
            return redirect('notifications:preferences')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NotificationPreferenceForm(instance=preference)

    # Get notification statistics
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    total_notifications = Notification.objects.filter(user=request.user).count()

    context = {
        'form': form,
        'unread_count': unread_count,
        'total_notifications': total_notifications,
        'preference': preference,
    }
    return render(request, 'notifications/preferences.html', context)


@login_required
def get_unread_count(request):
    """
    Get unread notifications count for badge (AJAX)
    """
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})


@login_required
def notification_detail(request, notification_id):
    """
    View notification details and mark as read
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)

    # Mark as read when viewing details
    if not notification.is_read:
        notification.mark_as_read()

    # Get related notifications
    related_notifications = Notification.objects.filter(
        user=request.user,
        notification_type=notification.notification_type
    ).exclude(id=notification_id).order_by('-created_at')[:5]

    context = {
        'notification': notification,
        'related_notifications': related_notifications,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
    }

    return render(request, 'notifications/detail.html', context)


@login_required
@require_http_methods(["POST"])
def bulk_action(request):
    """
    Handle bulk actions on notifications (mark read, delete, etc.)
    """
    try:
        data = json.loads(request.body)
        action = data.get('action')
        notification_ids = data.get('notification_ids', [])

        if not action or not notification_ids:
            return JsonResponse({
                'success': False,
                'message': 'Action and notification IDs are required'
            }, status=400)

        notifications = Notification.objects.filter(
            id__in=notification_ids,
            user=request.user
        )

        if action == 'mark_read':
            updated_count = notifications.update(is_read=True)
            message = f'Marked {updated_count} notifications as read'

        elif action == 'mark_unread':
            updated_count = notifications.update(is_read=False)
            message = f'Marked {updated_count} notifications as unread'

        elif action == 'delete':
            deleted_count, _ = notifications.delete()
            message = f'Deleted {deleted_count} notifications'

        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            }, status=400)

        return JsonResponse({
            'success': True,
            'message': message,
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def notification_feed(request):
    """
    AJAX endpoint for real-time notification feed (for dropdown)
    """
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    notifications_data = []
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%b %d, %Y %I:%M %p'),
            'time_ago': notification.get_time_ago(),
            'action_url': notification.action_url,
            'icon_class': notification.get_icon_class(),
        })

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({
        'success': True,
        'notifications': notifications_data,
        'unread_count': unread_count,
        'total_count': Notification.objects.filter(user=request.user).count()
    })


@login_required
@require_http_methods(["POST"])
def toggle_notification_preference(request, preference_type):
    """
    Quick toggle for notification preferences (AJAX)
    """
    try:
        preference = NotificationPreference.objects.get(user=request.user)
        field_name = preference_type

        if hasattr(preference, field_name):
            current_value = getattr(preference, field_name)
            setattr(preference, field_name, not current_value)
            preference.save()

            return JsonResponse({
                'success': True,
                'new_value': not current_value,
                'message': f'Preference updated successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid preference type'
            }, status=400)

    except NotificationPreference.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notification preferences not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def notification_statistics(request):
    """
    Get notification statistics for charts (AJAX)
    """
    # Last 30 days data
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

    # Notifications by type
    notifications_by_type = {}
    for notification_type, _ in Notification.NOTIFICATION_TYPES:
        count = Notification.objects.filter(
            user=request.user,
            notification_type=notification_type,
            created_at__gte=thirty_days_ago
        ).count()
        notifications_by_type[notification_type] = count

    # Notifications by day (last 7 days)
    daily_counts = []
    for i in range(6, -1, -1):
        day = timezone.now() - timezone.timedelta(days=i)
        count = Notification.objects.filter(
            user=request.user,
            created_at__date=day.date()
        ).count()
        daily_counts.append({
            'date': day.strftime('%Y-%m-%d'),
            'day': day.strftime('%a'),
            'count': count
        })

    # Read vs Unread ratio
    total_notifications = Notification.objects.filter(user=request.user).count()
    read_count = Notification.objects.filter(user=request.user, is_read=True).count()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return JsonResponse({
        'success': True,
        'notifications_by_type': notifications_by_type,
        'daily_counts': daily_counts,
        'read_ratio': {
            'read': read_count,
            'unread': unread_count,
            'total': total_notifications
        },
        'time_period': 'last_30_days'
    })


# Utility view for testing notifications
@login_required
@require_http_methods(["POST"])
def test_notification(request):
    """
    Create a test notification (for development)
    """
    try:
        data = json.loads(request.body)
        notification_type = data.get('type', 'system')
        title = data.get('title', 'Test Notification')
        message = data.get('message', 'This is a test notification')

        notification = create_notification(
            user=request.user,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url='/notifications/'
        )

        return JsonResponse({
            'success': True,
            'message': 'Test notification created successfully',
            'notification_id': notification.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)