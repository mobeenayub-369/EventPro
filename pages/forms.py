from django import forms
from .models import Page, FAQ, ContactSubmission


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'content', 'page_type',
            'meta_title', 'meta_description', 'is_active',
            'show_in_footer', 'show_in_navigation', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter page title'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'url-slug'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'page_type': forms.Select(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Meta title for SEO'}),
            'meta_description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Meta description for SEO'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if self.instance and self.instance.slug == slug:
            return slug
        if Page.objects.filter(slug=slug).exists():
            raise forms.ValidationError('A page with this slug already exists.')
        return slug


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['question', 'answer', 'category', 'order', 'is_active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter answer'}),
            'category': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'e.g., general, payments, events'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of your message',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'How can we help you?',
                'required': True
            }),
        }