from django.contrib import admin
from .models import *

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'processing_fee']
    list_editable = ['is_active']
    list_filter = ['is_active']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['transaction_id', 'user__username', 'booking__id']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20

@admin.register(JazzCashTransaction)
class JazzCashTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'pp_TxnRefNo', 'pp_ResponseCode', 'pp_TxnDateTime']
    search_fields = ['pp_TxnRefNo', 'transaction__transaction_id']

@admin.register(EasyPaisaTransaction)
class EasyPaisaTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'transaction_auth_id', 'response_code', 'mobile_account']
    search_fields = ['transaction_auth_id', 'mobile_account']

@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'bank_name', 'account_number', 'slip_number', 'transfer_date']
    search_fields = ['slip_number', 'bank_name']

@admin.register(CardTransaction)
class CardTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'card_type', 'card_number', 'authorization_code']
    search_fields = ['card_number', 'authorization_code']

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['transaction_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']

@admin.register(PaymentGatewaySettings)
class PaymentGatewaySettingsAdmin(admin.ModelAdmin):
    list_display = ['jazzcash_merchant_id', 'easypaisa_store_id', 'updated_at']