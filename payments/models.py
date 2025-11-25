from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Get the custom user model
User = get_user_model()

# Payment Model for handling payment transactions
class Payment(models.Model):
    # Payment status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]

    # Payment method choices
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('easypaisa', 'Easypaisa'),
        ('jazzcash', 'JazzCash'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    ]

    # STEP 9: FIX - Changed related_name to 'payment_info' to avoid clash with removed bookings.Payment
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='payment_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')

    # Payment amount and currency
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='PKR')
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Transaction references
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    gateway_reference = models.CharField(max_length=200, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Additional payment information
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # For storing gateway response data

    class Meta:
        ordering = ['-created_at']  # Newest payments first
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['transaction_id']),  # Faster transaction lookups
            models.Index(fields=['status', 'created_at']),  # Faster status-based queries
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.amount} {self.currency}"

    def mark_completed(self, transaction_id=None):
        """Mark payment as completed with transaction ID"""
        self.status = 'completed'
        self.transaction_id = transaction_id
        self.completed_at = timezone.now()
        self.save()

    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'completed'
    is_successful.boolean = True  # Enable boolean display in admin

    def get_status_display_with_color(self):
        """Get payment status with color coding for UI display"""
        status_colors = {
            'pending': 'warning',
            'completed': 'success',
            'failed': 'danger',
            'refunded': 'info',
            'cancelled': 'secondary',
        }
        return {
            'text': self.get_status_display(),
            'color': status_colors.get(self.status, 'secondary')
        }


# Refund Model for handling payment refunds
class Refund(models.Model):
    # Refund status choices
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]

    # Refund information
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')

    # Admin management fields
    admin_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='processed_refunds')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']  # Newest refunds first
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'

    def __str__(self):
        return f"Refund #{self.id} - {self.amount} PKR"