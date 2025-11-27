from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    """
    Form for creating and updating Category instances.
    Provides validation and custom widget configuration.
    """

    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']

        # Custom widgets for better UI and user experience
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name (e.g., Wedding, Conference)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter detailed description of this category',
                'rows': 3
            }),
        }

        # Custom labels for form fields
        labels = {
            'name': 'Category Name',
            'description': 'Description',
            'image': 'Category Image',
            'is_active': 'Active Status'
        }

        # Help text for form fields
        help_texts = {
            'name': 'Enter a unique name for the category',
            'description': 'Describe what type of events belong to this category',
            'is_active': 'Uncheck to hide this category from users'
        }