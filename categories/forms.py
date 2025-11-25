from django import forms
from .models import Category, Tag


# Category create/edit form with image upload validation
class CategoryForm(forms.ModelForm):
    """
    Form for creating and editing categories with image upload support
    Includes validation for image size and type
    """

    # IMAGE UPLOAD: Custom widget for better image upload UX
    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',  # Only accept image files
            'class': 'form-control-file',
        }),
        help_text="Upload a category image. Supported formats: JPG, PNG, GIF. Max size: 2MB"
    )

    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter category description...',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter category name...',
                'class': 'form-control'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'URL-friendly name (auto-generated)...',
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        # IMAGE UPLOAD: Help texts for better user guidance
        help_texts = {
            'image': 'Recommended size: 400x300 pixels. Will be cropped to fit.',
            'slug': 'Auto-generated from name. Only change if you need a specific URL.',
        }

    # IMAGE UPLOAD: Clean method to validate image
    def clean_image(self):
        """
        Validate uploaded image file
        - Check file size (max 2MB)
        - Check file type
        """
        image = self.cleaned_data.get('image')

        # If no image is uploaded, return None (keep existing or set to None)
        if not image:
            return None

        # Validate image size (2MB limit)
        if image.size > 2 * 1024 * 1024:  # 2MB in bytes
            raise forms.ValidationError('Image file too large ( > 2MB ). Please upload a smaller image.')

        # Validate file type
        valid_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in valid_content_types:
            raise forms.ValidationError('Unsupported file format. Please upload JPG, PNG, or GIF image.')

        return image

    # IMAGE UPLOAD: Auto-generate slug if empty
    def clean_slug(self):
        """
        Auto-generate slug from name if slug field is empty
        """
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')

        if not slug and name:
            from django.utils.text import slugify
            slug = slugify(name)

        return slug


# Tag create/edit form
class TagForm(forms.ModelForm):
    """
    Form for creating and editing tags
    Tags don't have images, only text-based information
    """

    class Meta:
        model = Tag
        fields = ['name', 'slug', 'description']

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter tag description...',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter tag name...',
                'class': 'form-control'
            }),
            'slug': forms.TextInput(attrs={
                'placeholder': 'URL-friendly name (auto-generated)...',
                'class': 'form-control'
            })
        }

        help_texts = {
            'slug': 'Auto-generated from name. Only change if you need a specific URL.',
        }

    # Auto-generate slug if empty
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')

        if not slug and name:
            from django.utils.text import slugify
            slug = slugify(name)

        return slug