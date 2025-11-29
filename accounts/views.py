from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm, LoginForm
from .models import CustomUser, UserProfile


# Register View
def register(request):
    """
    Handles user registration with form validation
    No image upload during registration for simplicity
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration Successful! Welcome to EventPro!')
                return redirect('home')
            except IntegrityError:
                messages.error(request, 'Username already exists. Please choose a different one.')
        else:
            # Form has errors, display them to user
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


# Login View with Bug Fixes
def login_view(request):
    """
    Handles user authentication with proper error handling
    Fixed the form.cleaned_get.data issue
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # FIX: Corrected form.cleaned_get.data to form.cleaned_data
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back {username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


# Profile View
@login_required
def profile(request):
    if request.method == 'POST':
        # Handle profile update here
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        return redirect('profile')

    return render(request, 'accounts/profile.html')


# Edit Profile View with Image Upload
@login_required
def edit_profile(request):
    """
    Handles profile editing with image upload functionality
    Supports profile picture upload and updates
    """
    if request.method == 'POST':
        # IMAGE UPLOAD: request.FILES is required for file uploads
        user_form = CustomUserChangeForm(
            request.POST,
            request.FILES,  # IMPORTANT: This handles file uploads
            instance=request.user
        )
        profile_form = UserProfileForm(
            request.POST,
            instance=request.user.userprofile
        )

        if user_form.is_valid() and profile_form.is_valid():
            try:
                # Save both forms
                user_form.save()
                profile_form.save()

                # IMAGE UPLOAD: Success message with image info
                if 'profile_picture' in request.FILES:
                    messages.success(request, 'Profile updated successfully with new picture!')
                else:
                    messages.success(request, 'Profile updated successfully!')

                return redirect('profile')

            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        else:
            # Form validation failed
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - initialize forms with current data
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/edit_profile.html', context)


# Public Profile View with Error Handling
def public_profile(request, username):
    """
    Displays public profile of any user
    Includes profile picture if available
    """
    try:
        user = get_object_or_404(CustomUser, username=username)
        return render(request, 'accounts/public_profile.html', {'user_profile': user})
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('home')


# Logout View
def logout_view(request):
    """
    Handles user logout with success message
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')