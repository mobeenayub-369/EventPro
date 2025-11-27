from django import forms
from .models import WishlistItem

class WishlistItemForm(forms.ModelForm):
    class Meta:
        model = WishlistItem
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about this event (optional)...'
            }),
        }

class WishlistShareForm(forms.Form):
    expires_in = forms.ChoiceField(
        choices=[
            (1, '1 Day'),
            (3, '3 Days'),
            (7, '1 Week'),
            (30, '1 Month'),
        ],
        initial=7,
        widget=forms.Select(attrs={'class': 'form-control'})
    )