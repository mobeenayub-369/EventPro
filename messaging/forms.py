from django import forms
from .models import Message

# Message Form
class MessageForm(forms.ModelForm):
    class Meta:
        model= Message
        fields= ['content']

        widgets= {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Type your message here...',
                'class': 'message-input'
            })
        }