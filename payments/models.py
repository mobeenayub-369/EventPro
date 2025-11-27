from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from events.models import Event
from bookings.models import Booking


class PaymentMethod(models.Model):
    PAYMENT_TYPES = (
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_debit_card', 'Credit/Debit Card'),
    )

    name = models.CharField(max_length=50, choices=PAYMENT_TYPES)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return self.get_name_display()


class Transaction(models.Model):
    TRANSACTION_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    # Payment Information
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='PKR')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)

    # Transaction Details
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')

    # Payment Gateway Response
    gateway_response = models.JSONField(null=True, blank=True)
    gateway_transaction_id = models.CharField(max_length=100, blank=True)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} PKR"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)

    def generate_transaction_id(self):
        import uuid
        return f"TXN{uuid.uuid4().hex[:12].upper()}"

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, reason=""):
        self.status = 'failed'
        self.gateway_response = {'failure_reason': reason}
        self.save()


class JazzCashTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    pp_Amount = models.CharField(max_length=20)
    pp_BillReference = models.CharField(max_length=100)
    pp_ResponseCode = models.CharField(max_length=10)
    pp_ResponseMessage = models.CharField(max_length=255)
    pp_TxnDateTime = models.CharField(max_length=20)
    pp_TxnRefNo = models.CharField(max_length=100)
    pp_RetreivalReferenceNo = models.CharField(max_length=100)

    def __str__(self):
        return f"JazzCash - {self.pp_TxnRefNo}"


class EasyPaisaTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    payment_token = models.CharField(max_length=255)
    mobile_account = models.CharField(max_length=15)
    transaction_auth_id = models.CharField(max_length=100)
    response_code = models.CharField(max_length=10)
    response_message = models.CharField(max_length=255)

    def __str__(self):
        return f"EasyPaisa - {self.transaction_auth_id}"


class BankTransfer(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    account_title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    transaction_slip = models.ImageField(upload_to='bank_slips/', null=True, blank=True)
    slip_number = models.CharField(max_length=100)
    transfer_date = models.DateField()

    def __str__(self):
        return f"Bank - {self.bank_name} - {self.slip_number}"


class CardTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20)  # Last 4 digits only
    card_type = models.CharField(max_length=20)  # visa, mastercard
    authorization_code = models.CharField(max_length=100)
    payment_gateway = models.CharField(max_length=50, default='stripe')  # or local gateway

    def __str__(self):
        return f"Card - {self.card_type} - {self.card_number}"


class Withdrawal(models.Model):
    WITHDRAWAL_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    )

    WITHDRAWAL_METHODS = (
        ('jazzcash', 'JazzCash'),
        ('easypaisa', 'EasyPaisa'),
        ('bank_transfer', 'Bank Transfer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=WITHDRAWAL_METHODS)
    account_details = models.JSONField()
    status = models.CharField(max_length=20, choices=WITHDRAWAL_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)

    admin_notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='processed_withdrawals')
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Withdrawal - {self.user.username} - {self.amount} PKR"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_withdrawal_id()
        super().save(*args, **kwargs)

    def generate_withdrawal_id(self):
        import uuid
        return f"WD{uuid.uuid4().hex[:10].upper()}"


class Refund(models.Model):
    REFUND_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    )

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='refunds')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    evidence = models.FileField(upload_to='refund_evidence/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=REFUND_STATUS, default='pending')
    admin_notes = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund - {self.transaction.transaction_id}"

    def save(self, *args, **kwargs):
        if not self.refund_amount:
            self.refund_amount = self.transaction.amount
        super().save(*args, **kwargs)


class PaymentGatewaySettings(models.Model):
    # JazzCash Settings
    jazzcash_merchant_id = models.CharField(max_length=100, blank=True)
    jazzcash_password = models.CharField(max_length=255, blank=True)
    jazzcash_integrity_salt = models.CharField(max_length=255, blank=True)
    jazzcash_live_mode = models.BooleanField(default=False)

    # EasyPaisa Settings
    easypaisa_store_id = models.CharField(max_length=100, blank=True)
    easypaisa_hash_key = models.CharField(max_length=255, blank=True)
    easypaisa_live_mode = models.BooleanField(default=False)

    # Bank Transfer Settings
    bank_name = models.CharField(max_length=100, blank=True)
    account_title = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    iban = models.CharField(max_length=34, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        try:
            return cls.objects.first() or cls()
        except:
            return cls()