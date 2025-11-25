from django import forms
from .models import SupportTicket, TicketResponse, FAQ

# Create support ticket form
class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = [
            'subject', 'description', 'ticket_type', 'priority'
        ]

        # Widgets Customization
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe your issue in detail...'
            }),
            'subject': forms.TextInput(attrs={
                'placeholder': 'Enter a brief subject for your ticket...'
            })
        }

    # Field customization
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['priority'].empty_label = None

# Ticket response form
class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ['message', 'attachment', 'is_internal_note']

        # Widgets Customization
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Type your response here...'
            })
        }

# FAQ form
class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'is_active', 'order']

        # Widgets Customization
        widgets = {
            'question': forms.TextInput(attrs={
                'placeholder': 'Enter frequently asked question...'
            }),
            'answer': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Enter the answer...'
            })
        }