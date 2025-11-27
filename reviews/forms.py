from django import forms
from .models import Review, ReviewVote


class ReviewForm(forms.ModelForm):
    """
    Form for creating and updating reviews with enhanced validation.
    """

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={
                'class': 'rating-radio',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this event... '
                               'What did you like? What could be improved?',
                'maxlength': 1000
            }),
        }
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review (Optional)'
        }
        help_texts = {
            'rating': 'How would you rate your experience with this event?',
            'comment': 'Your detailed feedback helps organizers improve their events'
        }

    def clean_rating(self):
        """Validate rating value."""
        rating = self.cleaned_data.get('rating')
        if rating not in [1, 2, 3, 4, 5]:
            raise forms.ValidationError("Please select a valid rating between 1 and 5.")
        return rating

    def clean_comment(self):
        """Validate comment length and content."""
        comment = self.cleaned_data.get('comment', '').strip()
        if comment and len(comment) < 10:
            raise forms.ValidationError("Please provide a more detailed review (at least 10 characters).")
        return comment


class ReviewResponseForm(forms.ModelForm):
    """
    Form for organizers to respond to reviews.
    """

    class Meta:
        model = Review
        fields = ['organizer_response']
        widgets = {
            'organizer_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Thank the reviewer and address their feedback...',
                'maxlength': 1000
            }),
        }
        labels = {
            'organizer_response': 'Your Response'
        }
        help_texts = {
            'organizer_response': 'Your response will be visible to all users viewing this review'
        }


class ReviewFilterForm(forms.Form):
    """
    Form for filtering and sorting reviews.
    """

    SORT_CHOICES = [
        ('newest', 'Newest First'),
        ('oldest', 'Oldest First'),
        ('highest', 'Highest Rating'),
        ('lowest', 'Lowest Rating'),
        ('most_helpful', 'Most Helpful'),
    ]

    RATING_CHOICES = [
        ('', 'All Ratings'),
        ('5', '⭐⭐⭐⭐⭐ Only'),
        ('4', '⭐⭐⭐⭐ & Above'),
        ('3', '⭐⭐⭐ & Above'),
        ('2', '⭐⭐ & Above'),
        ('1', '⭐ & Above'),
    ]

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='newest',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    min_rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        required=False,
        initial='',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    has_response = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='With Organizer Response Only'
    )