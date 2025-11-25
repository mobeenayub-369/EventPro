from django.urls import path
from . import views

urlpatterns = [
    # Payment URLs
    path('create/<int:booking_id>/', views.create_payment, name='create_payment'),
    path('process/<int:payment_id>/', views.process_payment, name='process_payment'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failure/<int:payment_id>/', views.payment_failure, name='payment_failure'),
    path('history/', views.payment_history, name='payment_history'),
    path('detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),

    # Refund URLs
    path('refund/request/<int:payment_id>/', views.request_refund, name='request_refund'),
    path('refund/history/', views.refund_history, name='refund_history'),

    # Webhook URLs (for payment gateways)
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]