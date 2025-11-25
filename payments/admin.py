from django.contrib import admin
from .models import Payment, Refund


# STEP 10: IMPLEMENTATION - Create new admin file for payments app
# This separates Payment admin from bookings admin to avoid conflicts

# Payment Admin Configuration
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Fields to display in admin list view
    list_display = ['id', 'booking', 'user', 'amount', 'payment_method', 'status', 'created_at']

    # Filter options for payment list
    list_filter = ['payment_method', 'status', 'created_at']

    # Searchable fields
    search_fields = ['transaction_id', 'booking__booking_id', 'user__username']

    # Read-only fields
    readonly_fields = ['created_at', 'updated_at']

    # Date-based navigation
    date_hierarchy = 'created_at'


# Refund Admin Configuration
@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    # Fields to display in admin list view
    list_display = ['id', 'payment', 'amount', 'status', 'created_at']

    # Filter options for refund list
    list_filter = ['status', 'created_at']

    # Searchable fields
    search_fields = ['payment__transaction_id', 'reason']