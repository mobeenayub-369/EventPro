from django import forms
from .models import Event, EventImage
from categories.models import Category, Tag


# Create/edit event form with comprehensive image validation
class EventForm(forms.ModelForm):
    """
    Form for creating and editing events with advanced image upload features
    Includes validation for multiple image types and file handling
    """

    # IMAGE UPLOAD: Custom widgets for better image upload UX
    main_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file image-upload',
            'data-max-size': '5MB'
        }),
        help_text="Upload main event banner (Max: 5MB, Recommended: 1200x600px)"
    )

    thumbnail = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file image-upload',
            'data-max-size': '2MB'
        }),
        help_text="Upload event thumbnail (Max: 2MB, Recommended: 400x300px)"
    )

    image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file image-upload',
            'data-max-size': '5MB'
        }),
        help_text="Upload event image (Max: 5MB)"
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'main_image', 'thumbnail', 'image', 'date', 'time',
            'location', 'price', 'capacity', 'category', 'tags', 'is_featured'
        ]

        # Widgets Customization
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your event in detail...',
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter event title...',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Enter event location or online link...',
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'class': 'form-control'
            }),
            'capacity': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

        # IMAGE UPLOAD: Help texts for better user guidance
        help_texts = {
            'main_image': 'This will be the primary image displayed on your event page.',
            'thumbnail': 'This image will be used in event lists and cards.',
            'image': 'General event image (fallback if others are not set).',
        }

    # Category and tags field customization
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['tags'].queryset = Tag.objects.all()  # FIXED: Corrected typo 'querset' to 'queryset'

        # IMAGE UPLOAD: Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['is_featured']:
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'

    # IMAGE UPLOAD: Validation for main image
    def clean_main_image(self):
        main_image = self.cleaned_data.get('main_image')
        return self._validate_image(main_image, 'main_image', 5)  # 5MB limit

    # IMAGE UPLOAD: Validation for thumbnail
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        return self._validate_image(thumbnail, 'thumbnail', 2)  # 2MB limit

    # IMAGE UPLOAD: Validation for general image
    def clean_image(self):
        image = self.cleaned_data.get('image')
        return self._validate_image(image, 'image', 5)  # 5MB limit

    # IMAGE UPLOAD: Common image validation method
    def _validate_image(self, image, field_name, max_size_mb):
        """
        Common validation method for all image fields
        - Checks file size
        - Validates file type
        - Provides helpful error messages
        """
        if not image:
            # If no new image uploaded, keep existing one
            if self.instance and self.instance.pk:
                existing_image = getattr(self.instance, field_name)
                if existing_image:
                    return existing_image
            return None

        # Validate image size
        max_size_bytes = max_size_mb * 1024 * 1024
        if image.size > max_size_bytes:
            raise forms.ValidationError(
                f'Image file too large (>{max_size_mb}MB). Please upload a smaller image.'
            )

        # Validate file type
        valid_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in valid_content_types:
            raise forms.ValidationError(
                'Unsupported file format. Please upload JPG, PNG, GIF, or WebP image.'
            )

        return image

    # IMAGE UPLOAD: Ensure at least one image is provided
    def clean(self):
        cleaned_data = super().clean()
        main_image = cleaned_data.get('main_image')
        thumbnail = cleaned_data.get('thumbnail')
        image = cleaned_data.get('image')

        # Check if at least one image is provided (for new events)
        if not self.instance.pk and not any([main_image, thumbnail, image]):
            raise forms.ValidationError(
                "Please upload at least one event image to make your event attractive."
            )

        return cleaned_data


# IMAGE UPLOAD: Form for adding media images
class EventImageForm(forms.ModelForm):
    """
    Form for adding additional media images to events
    """
    image = forms.ImageField(
        required=True,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control-file',
            'data-max-size': '5MB'
        }),
        help_text="Upload additional event photo (Max: 5MB)"
    )

    class Meta:
        model = EventImage
        fields = ['image', 'caption']

        widgets = {
            'caption': forms.TextInput(attrs={
                'placeholder': 'Optional caption for this image...',
                'class': 'form-control'
            })
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        return self._validate_image(image, 5)  # 5MB limit

    def _validate_image(self, image, max_size_mb):
        if not image:
            return None

        max_size_bytes = max_size_mb * 1024 * 1024
        if image.size > max_size_bytes:
            raise forms.ValidationError(f'Image file too large (>{max_size_mb}MB).')

        valid_content_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if image.content_type not in valid_content_types:
            raise forms.ValidationError('Unsupported file format.')

        return image