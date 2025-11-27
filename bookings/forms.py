from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Booking, BookingMessage, BookingRevision


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            # 'event_date',
            'event_time',
            'event_duration',
            # 'event_location',
            'number_of_guests',
            'special_requirements',
            'additional_charges',
            'discount_amount'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat()
            }),
            'event_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'event_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '24',
                'step': '1'
            }),
            'event_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full address or venue name'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Estimated number of attendees'
            }),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any special requests, dietary requirements, theme preferences, etc.',
                'rows': 4,
                'maxlength': '1000'
            }),
            'additional_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'discount_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            })
        }
        labels = {
            'event_date': 'Event Date *',
            'event_time': 'Event Time *',
            'event_duration': 'Duration (hours) *',
            'event_location': 'Event Location *',
            'number_of_guests': 'Number of Guests *',
            'special_requirements': 'Special Requirements',
            'additional_charges': 'Additional Charges ($)',
            'discount_amount': 'Discount Amount ($)'
        }
        help_texts = {
            'event_date': 'Select the date when your event will take place',
            'event_time': 'Select the start time for your event',
            'event_duration': 'How long will the event last?',
            'event_location': 'Where will the event be held?',
            'number_of_guests': 'Approximate number of people attending',
            'special_requirements': 'Any specific needs or preferences for your event',
            'additional_charges': 'Extra costs for transportation, equipment, etc.',
            'discount_amount': 'Any discount you want to apply'
        }

    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date < timezone.now().date():
            raise ValidationError('Event date cannot be in the past.')

        # Check if date is too far in the future (optional)
        max_future_date = timezone.now().date() + timezone.timedelta(days=365)  # 1 year max
        if event_date > max_future_date:
            raise ValidationError('Event date cannot be more than 1 year in the future.')

        return event_date

    def clean_number_of_guests(self):
        number_of_guests = self.cleaned_data.get('number_of_guests')
        if number_of_guests <= 0:
            raise ValidationError('Number of guests must be at least 1.')
        return number_of_guests

    def clean_event_duration(self):
        event_duration = self.cleaned_data.get('event_duration')
        if event_duration <= 0:
            raise ValidationError('Event duration must be at least 1 hour.')
        if event_duration > 24:
            raise ValidationError('Event duration cannot exceed 24 hours.')
        return event_duration

    def clean(self):
        cleaned_data = super().clean()
        additional_charges = cleaned_data.get('additional_charges', 0)
        discount_amount = cleaned_data.get('discount_amount', 0)

        if discount_amount > additional_charges:
            raise ValidationError({
                'discount_amount': 'Discount cannot be greater than additional charges.'
            })

        return cleaned_data


class BookingMessageForm(forms.ModelForm):
    class Meta:
        model = BookingMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your message here...',
                'rows': 3,
                'maxlength': '1000'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*,.pdf,.doc,.docx'
            })
        }
        labels = {
            'message': 'Message *',
            'attachment': 'Attachment (Optional)'
        }
        help_texts = {
            'message': 'Communicate with the other party about this booking',
            'attachment': 'Upload relevant documents or images (max 10MB)'
        }

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (10MB limit)
            if attachment.size > 10 * 1024 * 1024:
                raise ValidationError('File size must be less than 10MB.')

            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf',
                             'application/msword',
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if attachment.content_type not in allowed_types:
                raise ValidationError('File type not supported. Please upload images, PDF, or Word documents.')

        return attachment


class BookingRevisionForm(forms.ModelForm):
    class Meta:
        model = BookingRevision
        fields = ['revision_details', 'additional_cost']
        widgets = {
            'revision_details': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the changes you want to make to this booking...',
                'rows': 4,
                'maxlength': '500'
            }),
            'additional_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            })
        }
        labels = {
            'revision_details': 'Revision Details *',
            'additional_cost': 'Additional Cost ($)'
        }
        help_texts = {
            'revision_details': 'Clearly explain what changes you want to make',
            'additional_cost': 'Any extra cost for these changes (if applicable)'
        }

    def clean_additional_cost(self):
        additional_cost = self.cleaned_data.get('additional_cost')
        if additional_cost and additional_cost < 0:
            raise ValidationError('Additional cost cannot be negative.')
        return additional_cost


class BookingFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + Booking.BOOKING_STATUS_CHOICES
    ROLE_CHOICES = [
        ('', 'All Roles'),
        ('client', 'As Client'),
        ('provider', 'As Service Provider')
    ]

    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )

    role = forms.ChoiceField(
        required=False,
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'onchange': 'this.form.submit()'
        })
    )