from django import forms
from .models import Notification


# NOTIFICATION FORM FOR ADMIN
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'notification_type', 'title', 'message', 'related_object_id', 'related_object_type']


        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter notification message...'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter notification title...'
            })
        }