from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment Methods
    path('methods/', views.payment_methods, name='payment_methods'),

    # Payment Processing
    path('create/<int:booking_id>/', views.initiate_payment, name='create_payment'),
    path('process/<str:transaction_id>/', views.process_payment, name='process_payment'),
    path('jazzcash/<str:transaction_id>/', views.jazzcash_payment, name='jazzcash_payment'),
    path('easypaisa/<str:transaction_id>/', views.easypaisa_payment, name='easypaisa_payment'),
    path('bank-transfer/<str:transaction_id>/', views.bank_transfer_payment, name='bank_transfer_payment'),
    path('card/<str:transaction_id>/', views.card_payment, name='card_payment'),

    # Callbacks
    path('jazzcash-callback/', views.jazzcash_callback, name='jazzcash_callback'),
    path('easypaisa-callback/', views.easypaisa_callback, name='easypaisa_callback'),

    # Payment Status
    path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),
    path('failed/<str:transaction_id>/', views.payment_failed, name='payment_failure'),
    path('status/<str:transaction_id>/', views.payment_status, name='payment_detail'),

    # History & Management
    path('history/', views.payment_history, name='payment_history'),
    path('refund/request/', views.request_refund, name='request_refund'),
    path('refund/history/', views.refund_history, name='refund_history'),

    # Withdrawals
    path('withdrawal/request/', views.withdrawal_request, name='withdrawal_request'),
    path('withdrawal/history/', views.withdrawal_history, name='withdrawal_history'),

    # Analytics
    path('analytics/', views.payment_analytics, name='payment_analytics'),
]