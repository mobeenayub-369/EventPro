from django import forms
from django.contrib.auth.models import User
from .models import Message, Conversation, UserMessageSettings


class MessageForm(forms.ModelForm):
    """
    Form for sending messages with attachment support.
    """

    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message here...',
                'maxlength': 5000
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif'
            })
        }
        labels = {
            'content': 'Message',
            'attachment': 'Attach File'
        }
        help_texts = {
            'content': 'Maximum 5000 characters',
            'attachment': 'Supported formats: PDF, DOC, JPG, PNG, GIF (Max 10MB)'
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (10MB limit)
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 10MB.")

            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif']
            if not any(attachment.name.lower().endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError("Unsupported file format.")

        return attachment

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content and not self.cleaned_data.get('attachment'):
            raise forms.ValidationError("Message content or attachment is required.")
        return content


class NewConversationForm(forms.Form):
    """
    Form for starting a new conversation.
    """

    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Send To"
    )
    subject = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject (optional)'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Write your message...',
            'maxlength': 5000
        }),
        label="Message"
    )

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)

        if self.sender:
            # Exclude current user from recipient choices
            self.fields['recipient'].queryset = User.objects.exclude(id=self.sender.id)

    def clean_recipient(self):
        recipient = self.cleaned_data.get('recipient')
        if recipient == self.sender:
            raise forms.ValidationError("You cannot message yourself.")
        return recipient


class UserMessageSettingsForm(forms.ModelForm):
    """
    Form for user messaging settings.
    """

    class Meta:
        model = UserMessageSettings
        fields = [
            'email_notifications',
            'push_notifications',
            'allow_messages_from',
            'auto_responder_enabled',
            'auto_responder_message'
        ]
        widgets = {
            'auto_responder_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Set your auto-response message...',
                'maxlength': 1000
            }),
            'allow_messages_from': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'email_notifications': 'Receive email notifications for new messages',
            'push_notifications': 'Receive push notifications for new messages',
            'allow_messages_from': 'Allow messages from',
            'auto_responder_enabled': 'Enable auto-responder',
            'auto_responder_message': 'Auto-response message'
        }


class SearchMessagesForm(forms.Form):
    """
    Form for searching messages.
    """

    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search messages...'
        })
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="From Date"
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="To Date"
    )

    has_attachments = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Only show messages with attachments"
    )