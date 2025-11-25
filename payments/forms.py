from django import forms
from .models import Payment, Refund


# Payment Form
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'description']
        widgets = {
            'payment_method': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Additional payment notes (optional)...'
            })
        }


# Refund Request Form
class RefundRequestForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please explain why you are requesting a refund...',
                'required': 'required'
            })
        }

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if len(reason.strip()) < 10:
            raise forms.ValidationError("Please provide a detailed reason for refund (at least 10 characters).")
        return reason


# Admin Refund Processing Form
class RefundProcessingForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Admin notes regarding this refund...'
            })
        }