from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_messages', 'email_orders', 'email_reviews', 'email_promotions',
            'push_messages', 'push_orders', 'push_reviews'
        ]
        widgets = {
            'email_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_orders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_reviews': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_promotions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_messages': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_orders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'push_reviews': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }