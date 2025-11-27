from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Notification, NotificationPreference
import requests
import json


def create_notification(user, notification_type, title, message, sender=None, action_url=None, related_object=None):
    """
    Create a new notification for user
    """
    try:
        notification = Notification.objects.create(
            user=user,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url
        )

        # Get user preferences
        preference, created = NotificationPreference.objects.get_or_create(user=user)

        # Send email notification if enabled
        if should_send_email(preference, notification_type):
            send_email_notification(user, notification)

        # Send push notification if enabled
        if should_send_push(preference, notification_type):
            send_push_notification(user, notification)

        return notification

    except Exception as e:
        print(f"Error creating notification: {e}")
        return None


def should_send_email(preference, notification_type):
    """
    Check if email notification should be sent based on user preferences
    """
    email_preferences = {
        'message': preference.email_messages,
        'order': preference.email_orders,
        'review': preference.email_reviews,
        'system': True,  # Always send system notifications
        'promotion': preference.email_promotions,
        'reminder': True,  # Always send reminders
    }

    return email_preferences.get(notification_type, True)


def should_send_push(preference, notification_type):
    """
    Check if push notification should be sent based on user preferences
    """
    push_preferences = {
        'message': preference.push_messages,
        'order': preference.push_orders,
        'review': preference.push_reviews,
        'system': True,  # Always send system notifications
        'promotion': False,  # Don't send push for promotions by default
        'reminder': True,  # Always send reminders
    }

    return push_preferences.get(notification_type, True)


def send_email_notification(user, notification):
    """
    Send email notification to user
    """
    try:
        subject = f"EventPro - {notification.title}"

        # HTML email template
        html_message = render_to_string('notifications/email_notification.html', {
            'user': user,
            'notification': notification,
            'site_name': 'EventPro'
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True
        )

        return True

    except Exception as e:
        print(f"Error sending email notification: {e}")
        return False


def send_push_notification(user, notification):
    """
    Send push notification (placeholder for actual push service)
    """
    try:
        # This is a placeholder for actual push notification service
        # You can integrate with Firebase Cloud Messaging, OneSignal, etc.

        print(f"Push notification sent to {user.username}: {notification.title}")

        # Example for Firebase Cloud Messaging (FCM)
        # return send_fcm_notification(user, notification)

        return True

    except Exception as e:
        print(f"Error sending push notification: {e}")
        return False


def send_fcm_notification(user, notification):
    """
    Send push notification using Firebase Cloud Messaging
    """
    # This is an example implementation for FCM
    # You'll need to install: pip install pyfcm

    try:
        from pyfcm import FCMNotification

        # Initialize FCM
        push_service = FCMNotification(api_key=settings.FCM_API_KEY)

        # Get user's FCM registration token (you need to store this in user profile)
        registration_id = get_user_fcm_token(user)

        if not registration_id:
            return False

        message_title = notification.title
        message_body = notification.message

        # Additional data
        data_message = {
            "title": message_title,
            "body": message_body,
            "notification_type": notification.notification_type,
            "action_url": notification.action_url or "",
            "notification_id": str(notification.id)
        }

        # Send notification
        result = push_service.notify_single_device(
            registration_id=registration_id,
            message_title=message_title,
            message_body=message_body,
            data_message=data_message
        )

        return result.get('success', 0) > 0

    except ImportError:
        print("FCM not configured. Install pyfcm: pip install pyfcm")
        return False
    except Exception as e:
        print(f"FCM error: {e}")
        return False


def get_user_fcm_token(user):
    """
    Get user's FCM registration token from user profile
    """
    # You need to add fcm_token field to your User model or Profile model
    try:
        if hasattr(user, 'profile') and hasattr(user.profile, 'fcm_token'):
            return user.profile.fcm_token
        return None
    except:
        return None


def notify_event_created(event, creator):
    """
    Specialized function for event creation notifications
    """
    title = "Event Created Successfully"
    message = f"Your event '{event.title}' has been created and is now live."

    return create_notification(
        user=creator,
        notification_type='system',
        title=title,
        message=message,
        action_url=f'/events/{event.id}/'
    )


def notify_new_message(receiver, sender, message, conversation_id):
    """
    Specialized function for new message notifications
    """
    title = "New Message"
    message_text = f"You have a new message from {sender.username}"

    return create_notification(
        user=receiver,
        sender=sender,
        notification_type='message',
        title=title,
        message=message_text,
        action_url=f'/messages/{conversation_id}/'
    )


def notify_order_update(user, order, status):
    """
    Specialized function for order update notifications
    """
    title = "Order Updated"
    message = f"Your order #{order.id} status has been updated to {status}"

    return create_notification(
        user=user,
        notification_type='order',
        title=title,
        message=message,
        action_url=f'/orders/{order.id}/'
    )


def notify_new_review(user, reviewer, review, event):
    """
    Specialized function for new review notifications
    """
    title = "New Review"
    message = f"{reviewer.username} left a review for your event '{event.title}'"

    return create_notification(
        user=user,
        sender=reviewer,
        notification_type='review',
        title=title,
        message=message,
        action_url=f'/events/{event.id}/reviews/'
    )


def notify_promotional_offer(users, title, message, offer_url):
    """
    Send promotional notifications to multiple users
    """
    successful_notifications = 0

    for user in users:
        notification = create_notification(
            user=user,
            notification_type='promotion',
            title=title,
            message=message,
            action_url=offer_url
        )

        if notification:
            successful_notifications += 1

    return successful_notifications


def cleanup_old_notifications(days=30):
    """
    Clean up notifications older than specified days
    """
    from django.utils import timezone
    from django.db.models import Q

    cutoff_date = timezone.now() - timezone.timedelta(days=days)

    # Delete read notifications older than cutoff date
    deleted_count, _ = Notification.objects.filter(
        Q(is_read=True) & Q(created_at__lt=cutoff_date)
    ).delete()

    return deleted_count