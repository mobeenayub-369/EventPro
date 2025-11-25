from django import forms
from .models import Review, ReviewResponse, ReviewReport


# Review Creation Form
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'reviewed_at', 'image_1', 'image_2', 'image_3']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'title': forms.TextInput(attrs={
                'placeholder': 'Brief summary of your experience...',
                'maxlength': '200'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Share your detailed experience with this event...',
                'maxlength': '1000'
            }),
            'reviewed_at': forms.DateInput(attrs={'type': 'date'}),
            'image_1': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-upload'
            }),
            'image_2': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-upload'
            }),
            'image_3': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-upload'
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            raise forms.ValidationError("Please select a rating.")
        return rating

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title.strip()) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")
        return title

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment.strip()) < 50:
            raise forms.ValidationError("Please provide a more detailed review (at least 50 characters).")
        return comment

    def clean_image_1(self):
        image = self.cleaned_data.get('image_1')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image size must be less than 5MB.")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")
        return image

    def clean_image_2(self):
        image = self.cleaned_data.get('image_2')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image size must be less than 5MB.")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")
        return image

    def clean_image_3(self):
        image = self.cleaned_data.get('image_3')
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("Image size must be less than 5MB.")
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError("Please upload a valid image file.")
        return image


# Review Edit Form
class ReviewEditForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'image_1', 'image_2', 'image_3']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'title': forms.TextInput(attrs={'maxlength': '200'}),
            'comment': forms.Textarea(attrs={'rows': 6, 'maxlength': '1000'}),
            'image_1': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-upload'
            }),
            'image_2': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-upload'
            }),
            'image_3': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'image-upload'
            }),
        }


# Review Response Form
class ReviewResponseForm(forms.ModelForm):
    class Meta:
        model = ReviewResponse
        fields = ['response_text']
        widgets = {
            'response_text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a professional response to this review...',
                'maxlength': '500'
            })
        }

    def clean_response_text(self):
        response_text = self.cleaned_data.get('response_text')
        if len(response_text.strip()) < 10:
            raise forms.ValidationError("Response must be at least 10 characters long.")
        return response_text


# Review Report Form
class ReviewReportForm(forms.ModelForm):
    class Meta:
        model = ReviewReport
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.RadioSelect(choices=ReviewReport.REPORT_REASONS),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Please provide details about why you are reporting this review...',
                'maxlength': '500'
            })
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 20:
            raise forms.ValidationError("Please provide more details about your report (at least 20 characters).")
        return description