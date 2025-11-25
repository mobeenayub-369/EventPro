from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from events.models import Event
from bookings.models import Booking
from accounts.models import CustomUser

# ORGANIZER CHECK FUNCTION
def is_organizer(user):
    return user.user_type == 'organizer'

# CUSTOMER CHECK FUNCTION
def is_customer(user):
    return user.user_type == 'customer'

# MAIN DASHBOARD VIEW
@login_required
def dashboard_home(request):
    """Main Dashboard page based on user_type"""

    # USER TYPE CHECK
    if request.user.user_type == 'organizer':
        return organizer_dashboard(request)
    else:
        return customer_dashboard(request)


# Organizer Dashboard
@login_required
@user_passes_test(is_organizer)
def organizer_dashboard(request):
    """Dashboard for event organizers"""

    # Organizer Statistics
    total_events= Event.objects.filter(organizer= request.user).count()
    active_events= Event.objects.filter(organizer= request.user, is_active= True).count()
    total_bookings= Booking.objects.filter(event_organizer= request.user).count()


    # Revenue Calculation
    total_revenue= Booking.objects.filter(
        event_organizer= request.user,
        payment_status= 'paid'
    ).aggregate(Sum('total_amount'))['total_amount_sum'] or 0


    # Recent Events
    recent_events= Event.objects.filter(organizer= request.user).order_by('-created_at')[:5]

    # Recent Bookings
    recent_bookings= Booking.objects.filter(
        event_organizer= request.user
    ).select_related('user', 'event').order_by('-created_at')[:10]


    # Context Data (Send data to template)
    context= {
        'total_events': total_events,
        'active_events': active_events,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'recent_events': recent_events,
        'recent_bookings': recent_bookings,
    }

    return render(request,'dashboard/organizer_dashboard.html', context)


# Customer Dashboard
@login_required
@user_passes_test(is_customer)
def customer_dashboard(request):
    """Dashboard for customers"""

    # Customer Statistics
    total_bookings= Booking.objects.filter(user= request.user).count()
    upcoming_bookings= Booking.objects.filter(
        user= request.user,
        booking_status= 'confirmed'
    ).count()


    # Recent Bookings
    recent_bookings= Booking.objects.filter(user= request.user).select_related('event').order_by('-created_at')[:10]


    # Recommended Events
    user_categories= Event.objects.filter(
        booking_user= request.user
    ).value_list('category', flat= True).distinct()


    # Recommended Events Filter
    recommended_events= Event.objects.filter(
        category_in= user_categories,
        is_active= True
    ).exclude(booking_user= request.user).distinct()[:6]


    # Context Data(send data to Template)
    context= {
        'total_bookings': total_bookings,
        'upcoming_bookings': upcoming_bookings,
        'recent_bookings': recent_bookings,
        'recommended_events': recommended_events,
    }

    return render(request, 'dashboard/customer_dashboard.html', context)


# Organizer Event Management
@login_required
@user_passes_test(is_organizer)
def organizer_events(request):
    """Organizer's events management"""


    # Events Query
    events= Event.objects.filter(organizer= request.user).order_by('-created_at')

    return render(request, 'dashboard/organizer_events.html', {'events': events})


# Organizer Bookings Management
@login_required
@user_passes_test(is_organizer)
def organizer_bookings(request):
    """Organizer's bookings management"""


    # Bookings Query (of Organizers)
    bookings= Booking.objects.filter(event_organizer= request.user).select_related('user', 'event').order_by('-created_at')

    return render(request, 'dashboard/organizer_bookings.html', {'bookings': bookings})


# Customer Bookings
@login_required
def customer_bookings(request):
    """Customer's bookings"""


    # Booking Query (of Customers)
    bookings= Booking.objects.filter(user= request.user).select_related('event').order_by('-created_at')

    return render(request, 'dashboard/customer_bookings.html', {'bookings': bookings})


# Organizer Analytics
@login_required
@user_passes_test(is_organizer)
def organizer_analytics(request):
    """Organizer's analytics and reports"""


    # Monthly Revenue Imports
    from django.db.models.functions import TruncMonth

    # Monthly Revenue Query
    monthly_revenue= Booking.objects.filter(
        event_organizer= request.user,
        payment_status= 'paid'
    ).annotate(month= TruncMonth('created_at')).values('month').annotate(
        total= Sum('total_amount')
    ).order_by('month')


    # Event Performance
    event_performance= Event.objects.filter(organizer= request.user).annotate(
        bookings_count= Count('bookings'),
        total_revenue= Sum('bookings__total_amount')
    ).order_by('-bookings_count')[:10]


    # Context Data(send Analytics data to Template)
    context= {
        'monthly_revenue': monthly_revenue,
        'event_performance': event_performance,
    }


    return render(request, 'dashboard/organizer_analytics.html', context)