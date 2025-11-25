from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile


# User Registration Form
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    # IMAGE UPLOAD: No profile picture in registration to keep it simple
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'user_type', 'password1', 'password2')


# Profile Editing Form with Image Upload
class CustomUserChangeForm(UserChangeForm):
    # IMAGE UPLOAD: Custom widget for profile picture with better UX
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'accept': 'image/*',  # Accept only image files
            'class': 'form-control-file',
        }),
        help_text='Upload a clear profile picture. Max size: 2MB'
    )

    # IMAGE UPLOAD: Custom clean method for profile picture validation
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')

        # If no new image is uploaded, keep the existing one
        if not profile_picture:
            return self.instance.profile_picture

        # Validate image size (2MB limit)
        if profile_picture.size > 2 * 1024 * 1024:  # 2MB in bytes
            raise forms.ValidationError('Image file too large ( > 2MB )')

        # Validate file type
        if not profile_picture.content_type.startswith('image/'):
            raise forms.ValidationError('Please upload a valid image file')

        return profile_picture

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'bio',
                  'profile_picture', 'date_of_birth', 'address', 'city', 'country')

        # IMAGE UPLOAD: Custom labels and help texts
        help_texts = {
            'profile_picture': 'Recommended size: 200x200 pixels. Supported formats: JPG, PNG, GIF',
        }


# User Social Links Form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'facebook', 'instagram')


# Login Form
class LoginForm(forms.Form):
    # FIX: Corrected field name from 'user_name' to 'username' to match authentication
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )