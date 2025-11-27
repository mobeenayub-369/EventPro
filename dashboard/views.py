from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
import json

from .models import UserDashboard, DashboardWidget, UserActivity, DashboardMetric
from events.models import Event
from bookings.models import Booking
from payments.models import Transaction
from reviews.models import Review
from messaging.models import Message


@login_required
def dashboard_overview(request):
    """Main dashboard overview"""
    # Get or create user dashboard
    dashboard, created = UserDashboard.objects.get_or_create(user=request.user)
    dashboard.update_last_visited()

    # Calculate date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # User Statistics
    user_stats = {
        'total_events': Event.objects.filter(organizer=request.user).count(),
        'active_events': Event.objects.filter(organizer=request.user, is_active=True).count(),
        'total_bookings': Booking.objects.filter(user=request.user).count(),
        'upcoming_bookings': Booking.objects.filter(
            user=request.user,
            event__date__gte=today
        ).count(),
        'total_reviews': Review.objects.filter(user=request.user).count(),
        'unread_messages': Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count(),
    }

    # Revenue Statistics (for organizers)
    revenue_stats = {}
    if hasattr(request.user, 'is_organizer') and request.user.is_organizer:
        revenue_stats = {
            'total_revenue': Transaction.objects.filter(
                booking__event__organizer=request.user,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'monthly_revenue': Transaction.objects.filter(
                booking__event__organizer=request.user,
                status='completed',
                created_at__gte=month_ago
            ).aggregate(total=Sum('amount'))['total'] or 0,
            'weekly_revenue': Transaction.objects.filter(
                booking__event__organizer=request.user,
                status='completed',
                created_at__gte=week_ago
            ).aggregate(total=Sum('amount'))['total'] or 0,
        }

    # Recent Activities
    recent_activities = UserActivity.objects.filter(user=request.user)[:10]

    # Quick Stats Cards
    quick_stats = [
        {
            'title': 'My Events',
            'value': user_stats['total_events'],
            'icon': 'fas fa-calendar',
            'color': 'primary',
            'url': 'events:event_list'
        },
        {
            'title': 'Upcoming Bookings',
            'value': user_stats['upcoming_bookings'],
            'icon': 'fas fa-ticket-alt',
            'color': 'success',
            'url': 'bookings:booking_list'
        },
        {
            'title': 'Unread Messages',
            'value': user_stats['unread_messages'],
            'icon': 'fas fa-envelope',
            'color': 'warning',
            'url': 'messaging:inbox'
        },
        {
            'title': 'My Reviews',
            'value': user_stats['total_reviews'],
            'icon': 'fas fa-star',
            'color': 'info',
            'url': 'reviews:my_reviews'
        },
    ]

    # Add revenue stats for organizers
    if revenue_stats:
        quick_stats.extend([
            {
                'title': 'Total Revenue',
                'value': f"Rs. {revenue_stats['total_revenue']}",
                'icon': 'fas fa-money-bill-wave',
                'color': 'success',
                'url': 'payments:payment_analytics'
            },
            {
                'title': 'Monthly Revenue',
                'value': f"Rs. {revenue_stats['monthly_revenue']}",
                'icon': 'fas fa-chart-line',
                'color': 'primary',
                'url': 'payments:payment_analytics'
            }
        ])

    # Recent Events (for organizers)
    recent_events = Event.objects.filter(organizer=request.user).order_by('-created_at')[:5]

    # Upcoming Bookings
    upcoming_bookings = Booking.objects.filter(
        user=request.user,
        event__date__gte=today
    ).order_by('event__date')[:5]

    context = {
        'dashboard': dashboard,
        'user_stats': user_stats,
        'revenue_stats': revenue_stats,
        'quick_stats': quick_stats,
        'recent_activities': recent_activities,
        'recent_events': recent_events,
        'upcoming_bookings': upcoming_bookings,
        'active_tab': 'overview',
    }

    return render(request, 'dashboard/overview.html', context)


@login_required
def dashboard_analytics(request):
    """Advanced analytics dashboard"""
    dashboard, created = UserDashboard.objects.get_or_create(user=request.user)

    # Date ranges for analytics
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    three_months_ago = today - timedelta(days=90)

    # Booking trends (last 3 months)
    booking_trends = []
    for i in range(2, -1, -1):
        month_start = today.replace(day=1) - timedelta(days=30 * i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        monthly_bookings = Booking.objects.filter(
            user=request.user,
            created_at__date__range=[month_start, month_end]
        ).count()

        booking_trends.append({
            'month': month_start.strftime('%b %Y'),
            'bookings': monthly_bookings
        })

    # Event categories distribution
    category_stats = Event.objects.filter(
        organizer=request.user
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')[:8]

    # Revenue trends (for organizers)
    revenue_trends = []
    if hasattr(request.user, 'is_organizer') and request.user.is_organizer:
        for i in range(2, -1, -1):
            month_start = today.replace(day=1) - timedelta(days=30 * i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            monthly_revenue = Transaction.objects.filter(
                booking__event__organizer=request.user,
                status='completed',
                created_at__date__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))['total'] or 0

            revenue_trends.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(monthly_revenue)
            })

    # Activity heatmap (last 30 days)
    activity_heatmap = []
    for i in range(29, -1, -1):
        date = today - timedelta(days=i)
        daily_activities = UserActivity.objects.filter(
            user=request.user,
            created_at__date=date
        ).count()

        activity_heatmap.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%a'),
            'activities': daily_activities,
            'intensity': min(daily_activities, 10)  # Cap at 10 for visualization
        })

    context = {
        'dashboard': dashboard,
        'booking_trends': booking_trends,
        'category_stats': category_stats,
        'revenue_trends': revenue_trends,
        'activity_heatmap': activity_heatmap,
        'active_tab': 'analytics',
    }

    return render(request, 'dashboard/analytics.html', context)


@login_required
def dashboard_simple(request):
    """Simple/minimal dashboard view"""
    dashboard, created = UserDashboard.objects.get_or_create(user=request.user)

    # Basic stats for simple view
    today = timezone.now().date()

    simple_stats = {
        'today_bookings': Booking.objects.filter(
            user=request.user,
            created_at__date=today
        ).count(),
        'week_bookings': Booking.objects.filter(
            user=request.user,
            created_at__date__gte=today - timedelta(days=7)
        ).count(),
        'month_events': Event.objects.filter(
            organizer=request.user,
            created_at__date__gte=today - timedelta(days=30)
        ).count(),
    }

    # Recent important activities
    recent_important = UserActivity.objects.filter(
        user=request.user,
        activity_type__in=['booking_made', 'payment_made', 'event_created']
    )[:5]

    context = {
        'dashboard': dashboard,
        'simple_stats': simple_stats,
        'recent_important': recent_important,
        'active_tab': 'simple',
    }

    return render(request, 'dashboard/simple.html', context)


@login_required
def update_dashboard_preferences(request):
    """Update user dashboard preferences"""
    if request.method == 'POST':
        dashboard = get_object_or_404(UserDashboard, user=request.user)
        preferred_view = request.POST.get('preferred_view')

        if preferred_view in ['overview', 'analytics', 'simple']:
            dashboard.preferred_view = preferred_view
            dashboard.save()

            return JsonResponse({
                'success': True,
                'message': 'Dashboard preferences updated successfully!'
            })

    return JsonResponse({'success': False, 'message': 'Invalid request.'})


@login_required
def get_dashboard_stats(request):
    """Get real-time dashboard stats (AJAX)"""
    today = timezone.now().date()

    stats = {
        'unread_messages': Message.objects.filter(
            receiver=request.user,
            is_read=False
        ).count(),
        'pending_bookings': Booking.objects.filter(
            user=request.user,
            status='pending'
        ).count(),
        'today_activities': UserActivity.objects.filter(
            user=request.user,
            created_at__date=today
        ).count(),
    }

    return JsonResponse(stats)


# Utility function to log user activities
def log_user_activity(user, activity_type, description, request=None):
    """Log user activity for dashboard"""
    ip_address = None
    user_agent = ''

    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip