from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Booking creation and listing
    path('', views.booking_list, name='booking_list'),
    path('create/<int:event_id>/', views.create_booking, name='create_booking'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),

    # Booking actions
    path('<int:pk>/update-status/<str:action>/', views.update_booking_status, name='update_booking_status'),
    path('<int:pk>/send-message/', views.send_booking_message, name='send_booking_message'),
    path('<int:pk>/request-revision/', views.request_booking_revision, name='request_booking_revision'),

    # Additional views
    path('calendar/', views.booking_calendar, name='booking_calendar'),

    # API endpoints (for AJAX)
    # path('api/bookings/', views.booking_list_api, name='booking_list_api'),
    # path('api/bookings/<int:pk>/', views.booking_detail_api, name='booking_detail_api'),
]
