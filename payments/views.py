from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.conf import settings
import json
import hashlib
import requests
import uuid

from .models import *
from .forms import BankTransferForm, WithdrawalForm, RefundRequestForm, CardPaymentForm
from bookings.models import Booking
from events.models import Event


# Utility Functions
def create_transaction(booking, user, payment_method, amount):
    """Create a new transaction"""
    transaction = Transaction.objects.create(
        booking=booking,
        user=user,
        amount=amount,
        payment_method=payment_method,
        status='pending'
    )
    return transaction


def verify_jazzcash_payment(data):
    """Verify JazzCash payment response"""
    try:
        settings = PaymentGatewaySettings.get_settings()
        hash_data = f"{settings.jazzcash_integrity_salt}{data.get('pp_Amount')}{data.get('pp_BillReference')}{data.get('pp_ResponseCode')}{settings.jazzcash_password}"
        expected_hash = hashlib.sha256(hash_data.encode()).hexdigest().upper()
        return expected_hash == data.get('pp_SecureHash')
    except:
        return False


@login_required
def payment_methods(request):
    """Display available payment methods"""
    methods = PaymentMethod.objects.filter(is_active=True)

    context = {
        'payment_methods': methods,
        'active_tab': 'payment_methods'
    }
    return render(request, 'payments/payment_methods.html', context)


@login_required
def initiate_payment(request, booking_id):
    """Initiate payment for a booking - for create_payment.html"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        payment_method_id = request.POST.get('payment_method')
        payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, is_active=True)

        # Create transaction
        transaction = create_transaction(booking, request.user, payment_method, booking.total_amount)

        # Redirect based on payment method
        if payment_method.name == 'jazzcash':
            return redirect('payments:jazzcash_payment', transaction_id=transaction.transaction_id)
        elif payment_method.name == 'easypaisa':
            return redirect('payments:easypaisa_payment', transaction_id=transaction.transaction_id)
        elif payment_method.name == 'bank_transfer':
            return redirect('payments:bank_transfer_payment', transaction_id=transaction.transaction_id)
        elif payment_method.name == 'credit_debit_card':
            return redirect('payments:card_payment', transaction_id=transaction.transaction_id)

    methods = PaymentMethod.objects.filter(is_active=True)

    context = {
        'booking': booking,
        'payment_methods': methods,
    }
    return render(request, 'payments/create_payment.html', context)


@login_required
def process_payment(request, transaction_id):
    """Generic payment processing - for process_payment.html"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    # If already completed, redirect to success
    if transaction.status == 'completed':
        return redirect('payments:payment_success', transaction_id=transaction.transaction_id)

    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/process_payment.html', context)


@login_required
def jazzcash_payment(request, transaction_id):
    """Process JazzCash payment"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    settings = PaymentGatewaySettings.get_settings()

    # Convert amount to paisas
    amount = int(float(transaction.amount) * 100)

    # Create secure hash
    hash_data = f"{settings.jazzcash_integrity_salt}{settings.jazzcash_merchant_id}{transaction.transaction_id}{amount}{settings.jazzcash_password}"
    secure_hash = hashlib.sha256(hash_data.encode()).hexdigest().upper()

    context = {
        'transaction': transaction,
        'merchant_id': settings.jazzcash_merchant_id,
        'amount': amount,
        'transaction_id': transaction.transaction_id,
        'secure_hash': secure_hash,
        'return_url': request.build_absolute_uri('/payments/jazzcash-callback/'),
        'live_mode': settings.jazzcash_live_mode,
    }

    return render(request, 'payments/jazzcash_payment.html', context)


@login_required
def easypaisa_payment(request, transaction_id):
    """Process EasyPaisa payment"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    settings = PaymentGatewaySettings.get_settings()

    context = {
        'transaction': transaction,
        'store_id': settings.easypaisa_store_id,
        'amount': transaction.amount,
        'return_url': request.build_absolute_uri('/payments/easypaisa-callback/'),
        'live_mode': settings.easypaisa_live_mode,
    }

    return render(request, 'payments/easypaisa_payment.html', context)


@login_required
def bank_transfer_payment(request, transaction_id):
    """Bank transfer payment instructions"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    settings = PaymentGatewaySettings.get_settings()

    if request.method == 'POST':
        form = BankTransferForm(request.POST, request.FILES)
        if form.is_valid():
            bank_transfer = form.save(commit=False)
            bank_transfer.transaction = transaction
            bank_transfer.save()

            # Update transaction status to pending verification
            transaction.status = 'pending'
            transaction.save()

            messages.success(request,
                             'Bank transfer details submitted successfully! We will verify your payment within 24 hours.')
            return redirect('payments:payment_status', transaction_id=transaction.transaction_id)
    else:
        form = BankTransferForm()

    context = {
        'transaction': transaction,
        'bank_details': settings,
        'form': form,
    }
    return render(request, 'payments/bank_transfer.html', context)


@login_required
def card_payment(request, transaction_id):
    """Credit/Debit card payment"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    if request.method == 'POST':
        form = CardPaymentForm(request.POST)
        if form.is_valid():
            # Simulate card payment processing
            card_data = form.cleaned_data

            try:
                # In real implementation, integrate with payment gateway like Stripe, Paymob, etc.
                transaction.mark_completed()

                # Create card transaction record
                CardTransaction.objects.create(
                    transaction=transaction,
                    card_number=card_data['card_number'][-4:],
                    card_type='visa' if card_data['card_number'].startswith('4') else 'mastercard',
                    authorization_code=f"AUTH{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    payment_gateway='simulated'
                )

                messages.success(request, 'Payment completed successfully!')
                return redirect('payments:payment_success', transaction_id=transaction.transaction_id)

            except Exception as e:
                transaction.mark_failed(str(e))
                messages.error(request, f'Payment failed: {str(e)}')
                return redirect('payments:payment_failure', transaction_id=transaction.transaction_id)
    else:
        form = CardPaymentForm()

    context = {
        'transaction': transaction,
        'form': form,
    }
    return render(request, 'payments/card_payment.html', context)


@csrf_exempt
def jazzcash_callback(request):
    """JazzCash payment callback handler"""
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            transaction_id = data.get('pp_TxnRefNo')

            if not verify_jazzcash_payment(data):
                return redirect('payments:payment_failure', transaction_id=transaction_id)

            transaction = get_object_or_404(Transaction, transaction_id=transaction_id)

            # Save JazzCash transaction details
            JazzCashTransaction.objects.create(
                transaction=transaction,
                pp_Amount=data.get('pp_Amount'),
                pp_BillReference=data.get('pp_BillReference'),
                pp_ResponseCode=data.get('pp_ResponseCode'),
                pp_ResponseMessage=data.get('pp_ResponseMessage'),
                pp_TxnDateTime=data.get('pp_TxnDateTime'),
                pp_TxnRefNo=transaction_id,
                pp_RetreivalReferenceNo=data.get('pp_RetreivalReferenceNo')
            )

            response_code = data.get('pp_ResponseCode')
            if response_code == '000':
                transaction.mark_completed()
                return redirect('payments:payment_success', transaction_id=transaction_id)
            else:
                transaction.mark_failed(data.get('pp_ResponseMessage'))
                return redirect('payments:payment_failure', transaction_id=transaction_id)

        except Exception as e:
            print(f"JazzCash callback error: {e}")

    return redirect('payments:payment_failure')


@csrf_exempt
def easypaisa_callback(request):
    """EasyPaisa payment callback handler"""
    if request.method == 'POST':
        try:
            data = request.POST.dict()
            transaction_id = data.get('orderId')

            transaction = get_object_or_404(Transaction, transaction_id=transaction_id)

            # Verify payment (simplified - implement actual verification)
            if data.get('responseCode') == '0000':
                transaction.mark_completed()

                EasyPaisaTransaction.objects.create(
                    transaction=transaction,
                    payment_token=data.get('paymentToken'),
                    mobile_account=data.get('msisdn'),
                    transaction_auth_id=data.get('authId'),
                    response_code='0000',
                    response_message='Success'
                )

                return redirect('payments:payment_success', transaction_id=transaction_id)
            else:
                transaction.mark_failed(data.get('responseMessage', 'Payment failed'))
                return redirect('payments:payment_failure', transaction_id=transaction_id)

        except Exception as e:
            print(f"EasyPaisa callback error: {e}")

    return redirect('payments:payment_failure')


@login_required
def payment_success(request, transaction_id):
    """Payment success page - for payment_success.html"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    # Update booking status if payment is completed
    if transaction.status == 'completed':
        transaction.booking.status = 'confirmed'
        transaction.booking.save()

    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_failure(request, transaction_id):
    """Payment failed page - for payment_failure.html"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/payment_failure.html', context)


@login_required
def payment_status(request, transaction_id):
    """Check payment status - for payment_detail.html"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)

    context = {
        'transaction': transaction,
    }
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_history(request):
    """User payment history - for payment_history.html"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(transactions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_spent = Transaction.objects.filter(
        user=request.user,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    successful_payments = transactions.filter(status='completed').count()
    failed_payments = transactions.filter(status='failed').count()

    context = {
        'transactions': page_obj,
        'total_spent': total_spent,
        'successful_payments': successful_payments,
        'failed_payments': failed_payments,
        'total_payments': transactions.count(),
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def request_refund(request):
    """Request refund - for request_refund.html"""
    user_transactions = Transaction.objects.filter(
        user=request.user,
        status='completed'
    ).order_by('-created_at')

    if request.method == 'POST':
        form = RefundRequestForm(request.POST, request.FILES)
        if form.is_valid():
            transaction_id = form.cleaned_data['transaction_id']
            reason = form.cleaned_data['reason']
            evidence = form.cleaned_data['evidence']

            try:
                transaction = Transaction.objects.get(
                    transaction_id=transaction_id,
                    user=request.user,
                    status='completed'
                )

                # Check if refund is possible (within 7 days)
                days_since_payment = (timezone.now() - transaction.completed_at).days
                if days_since_payment > 7:
                    messages.error(request, 'Refund request must be made within 7 days of payment.')
                    return redirect('payments:request_refund')

                # Create refund request (you can create a Refund model)
                # Refund.objects.create(transaction=transaction, reason=reason, evidence=evidence)

                messages.success(request,
                                 'Refund request submitted successfully! We will process it within 3-5 business days.')
                return redirect('payments:refund_history')

            except Transaction.DoesNotExist:
                messages.error(request, 'Transaction not found or not eligible for refund.')
    else:
        form = RefundRequestForm()

    context = {
        'form': form,
        'transactions': user_transactions,
    }
    return render(request, 'payments/request_refund.html', context)


@login_required
def refund_history(request):
    """Refund history - for refund_history.html"""
    # Placeholder - create Refund model to store refund requests
    refunds = []  # Refund.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'refunds': refunds,
    }
    return render(request, 'payments/refund_history.html', context)


@login_required
def withdrawal_request(request):
    """Request withdrawal"""
    # Calculate available balance
    completed_transactions = Transaction.objects.filter(
        booking__event__organizer=request.user,
        status='completed'
    )
    total_earnings = completed_transactions.aggregate(total=Sum('amount'))['total'] or 0

    pending_withdrawals = Withdrawal.objects.filter(
        user=request.user,
        status__in=['pending', 'approved']
    ).aggregate(total=Sum('amount'))['total'] or 0

    available_balance = total_earnings - pending_withdrawals

    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            withdrawal = form.save(commit=False)
            withdrawal.user = request.user

            if withdrawal.amount > available_balance:
                messages.error(request, 'Insufficient balance for withdrawal.')
            elif withdrawal.amount < 500:
                messages.error(request, 'Minimum withdrawal amount is 500 PKR.')
            else:
                withdrawal.save()
                messages.success(request,
                                 'Withdrawal request submitted successfully! It will be processed within 3-5 business days.')
                return redirect('payments:withdrawal_history')
    else:
        form = WithdrawalForm()

    context = {
        'form': form,
        'available_balance': available_balance,
        'total_earnings': total_earnings,
        'pending_withdrawals': pending_withdrawals,
    }
    return render(request, 'payments/withdrawal_request.html', context)


@login_required
def withdrawal_history(request):
    """Withdrawal request history"""
    withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'withdrawals': withdrawals,
    }
    return render(request, 'payments/withdrawal_history.html', context)


@login_required
def payment_analytics(request):
    """Payment analytics for sellers"""
    # Calculate earnings
    completed_transactions = Transaction.objects.filter(
        booking__event__organizer=request.user,
        status='completed'
    )

    total_earnings = completed_transactions.aggregate(total=Sum('amount'))['total'] or 0
    pending_withdrawals = Withdrawal.objects.filter(
        user=request.user,
        status__in=['pending', 'approved']
    ).aggregate(total=Sum('amount'))['total'] or 0
    available_balance = total_earnings - pending_withdrawals

    # Monthly earnings
    monthly_earnings = completed_transactions.filter(
        created_at__month=timezone.now().month,
        created_at__year=timezone.now().year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Payment method distribution
    payment_method_stats = completed_transactions.values(
        'payment_method__name'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    context = {
        'total_earnings': total_earnings,
        'pending_withdrawals': pending_withdrawals,
        'available_balance': available_balance,
        'monthly_earnings': monthly_earnings,
        'payment_method_stats': payment_method_stats,
        'total_transactions': completed_transactions.count(),
    }
    return render(request, 'payments/analytics.html', context)


# Admin Views
@login_required
def admin_payment_list(request):
    """Admin view for all payments (for organizers)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')

    transactions = Transaction.objects.all().order_by('-created_at')

    # Filters
    status_filter = request.GET.get('status', '')
    method_filter = request.GET.get('method', '')

    if status_filter:
        transactions = transactions.filter(status=status_filter)
    if method_filter:
        transactions = transactions.filter(payment_method__name=method_filter)

    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
        'status_filter': status_filter,
        'method_filter': method_filter,
    }
    return render(request, 'payments/admin_payment_list.html', context)


@login_required
def admin_withdrawal_list(request):
    """Admin view for withdrawal requests"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')

    withdrawals = Withdrawal.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status', '')

    if status_filter:
        withdrawals = withdrawals.filter(status=status_filter)

    context = {
        'withdrawals': withdrawals,
        'status_filter': status_filter,
    }
    return render(request, 'payments/admin_withdrawal_list.html', context)


@login_required
def update_withdrawal_status(request, withdrawal_id):
    """Update withdrawal status (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    if request.method == 'POST':
        withdrawal = get_object_or_404(Withdrawal, id=withdrawal_id)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')

        if new_status in dict(Withdrawal.WITHDRAWAL_STATUS_CHOICES):
            withdrawal.status = new_status
            withdrawal.admin_notes = notes
            withdrawal.processed_by = request.user
            withdrawal.processed_at = timezone.now()
            withdrawal.save()

            return JsonResponse({'success': True, 'message': 'Withdrawal status updated successfully.'})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})