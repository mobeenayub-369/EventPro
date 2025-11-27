from django import forms
from .models import BankTransfer, Withdrawal, Transaction


class BankTransferForm(forms.ModelForm):
    class Meta:
        model = BankTransfer
        fields = ['bank_name', 'account_title', 'account_number', 'slip_number', 'transfer_date', 'transaction_slip']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., HBL, UBL, MCB'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your account number'}),
            'slip_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction slip number'}),
        }


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'method', 'account_details']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '500', 'step': '100'}),
            'method': forms.Select(attrs={'class': 'form-control'}),
            'account_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your JazzCash/EasyPaisa number or bank account details'
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount < 500:
            raise forms.ValidationError("Minimum withdrawal amount is 500 PKR")
        return amount


class RefundRequestForm(forms.Form):
    transaction_id = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    reason = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    evidence = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class CardPaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'pattern': '[0-9]{13,19}'
        })
    )
    expiry_date = forms.CharField(
        max_length=7,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YYYY',
            'pattern': '(0[1-9]|1[0-2])/[0-9]{4}'
        })
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'pattern': '[0-9]{3,4}'
        })
    )
    card_holder = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Card Holder Name'
        })
    )