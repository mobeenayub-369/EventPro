from django import forms
from django.core.exceptions import ValidationError
from .models import Event, EventImage, EventReview


class EventForm(forms.ModelForm):
    # Additional form fields for multiple images
    primary_image = forms.ImageField(
        required=True,
        label='Primary Event Image *',
        help_text='This will be the main display image for your event service',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    image_2 = forms.ImageField(
        required=False,
        label='Additional Image 2',
        help_text='Show another aspect of your event organization',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    image_3 = forms.ImageField(
        required=False,
        label='Additional Image 3',
        help_text='More images help attract more clients',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    image_4 = forms.ImageField(
        required=False,
        label='Additional Image 4',
        help_text='Show your best work',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'price',
            'capacity', 'duration', 'location', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'e.g., Professional Wedding Event Planning',
                'maxlength': '200'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your event organization services in detail. Include your experience, what makes you unique, and what clients can expect...',
                'rows': 6,
                'maxlength': '2000'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'min': '0',
                'step': '0.01'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 100',
                'min': '1'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 4',
                'min': '1'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Karachi, Pakistan or Multiple Locations'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'title': 'Event Service Title *',
            'description': 'Service Description *',
            'event_type': 'Event Type *',
            'price': 'Starting Price ($) *',
            'capacity': 'Event Capacity',
            'duration': 'Duration (hours)',
            'location': 'Service Location',
            'status': 'Status'
        }
        help_texts = {
            'title': 'Make it clear and attractive to potential clients',
            'description': 'Be detailed about what you offer and your experience',
            'price': 'Base starting price for your event service',
            'capacity': 'Maximum number of attendees you can handle',
            'duration': 'Typical event duration in hours',
            'location': 'Where you primarily provide services'
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise ValidationError('Title must be at least 10 characters long.')
        return title

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError('Price must be greater than 0.')
        return price

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity <= 0:
            raise ValidationError('Capacity must be greater than 0.')
        return capacity

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration and duration <= 0:
            raise ValidationError('Duration must be greater than 0.')
        return duration


class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ['image', 'caption', 'is_primary', 'display_order']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional image caption...',
                'maxlength': '200'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            })
        }


class EventReviewForm(forms.ModelForm):
    class Meta:
        model = EventReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=EventReview.RATING_CHOICES),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with this event service...',
                'rows': 4,
                'maxlength': '1000'
            })
        }
        labels = {
            'rating': 'Your Rating *',
            'comment': 'Your Review (Optional)'
        }


class EventSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for event services...',
            'aria-label': 'Search events'
        })
    )

    event_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Event Types')] + Event.EVENT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'step': '0.01'
        })
    )

    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'step': '0.01'
        })
    )

    min_capacity = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min capacity'
        })
    )

    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('price', 'Price: Low to High'),
        ('-price', 'Price: High to Low'),
        ('-average_rating', 'Highest Rated'),
        ('-view_count', 'Most Popular'),
    ]

    sort = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        initial='-created_at',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )