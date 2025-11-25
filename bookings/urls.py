from django.urls import path
from . import views

urlpatterns= [
    path('', views.my_bookings, name='my_bookings'),
    path('create/<int:event_id>', views.create_booking, name='create_booking'),
    path('<int:booking_id>', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/payment', views.booking_payment, name='booking_payment'),
    path('<int:booking_id>/cancel', views.cancel_booking, name='cancel_booking'),
    path('<int:booking_id>/invoice', views.booking_invoice, name='booking_invoice'),
]