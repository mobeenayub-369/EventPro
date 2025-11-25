from django import forms
from .models import Page


# Page creation/edit form
class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'content', 'meta_title', 'meta_description',
            'status', 'show_in_footer', 'show_in_header', 'order'
        ]

        # Widget customization for better UX
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Enter page content...',
                'class': 'rich-text-editor'
            }),
            'meta_description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Brief description for SEO...'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter page title...'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'url-friendly-version'
            })
        }

    # Form initialization
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Help texts for better guidance
        self.fields['slug'].help_text = "URL-friendly version of the title (auto-generated if left empty)"
        self.fields['order'].help_text = "Lower numbers appear first in navigation"