from django.urls import path
from . import views

urlpatterns= [
    path('', views.dashboard_home, name='dashboard'),
    path('organizer/events/', views.organizer_events, name= 'organizer_events'),
    path('organizer/bookings/', views.organizer_bookings, name='organizer_bookings'),
    path('organizer/analytics/', views.organizer_analytics, name='organizer_analytics'),
    path('customer/bookings/', views.customer_bookings, name= 'customer_bookings'),
]