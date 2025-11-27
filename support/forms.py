from django import forms
from .models import SupportTicket, TicketResponse, KnowledgeBaseArticle


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['category', 'subject', 'description', 'priority', 'attachment']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of your issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Please provide detailed information about your issue...'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if len(subject) < 10:
            raise forms.ValidationError("Subject must be at least 10 characters long.")
        return subject


class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketResponse
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your response here...'
            }),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBaseArticle
        fields = ['category', 'title', 'slug', 'content', 'is_published']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }