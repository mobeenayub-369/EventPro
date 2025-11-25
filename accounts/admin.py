from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


# Custom User Admin with Image Support
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Display fields in admin list view
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['is_verified', 'is_active']

    # IMAGE UPLOAD: Readonly field to display profile picture in admin
    readonly_fields = ['profile_picture_preview']

    def profile_picture_preview(self, obj):
        """
        Displays profile picture thumbnail in admin
        """
        if obj.profile_picture:
            return f'<img src="{obj.profile_picture.url}" width="50" height="50" style="border-radius: 50%;" />'
        return "No Image"

    profile_picture_preview.short_description = 'Profile Picture Preview'
    profile_picture_preview.allow_tags = True

    # Fieldsets for add/edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': (
                'user_type', 'phone_number', 'profile_picture', 'profile_picture_preview',
                'bio', 'date_of_birth', 'address', 'city', 'country', 'is_verified'
            )
        }),
    )

    # Fields to show when adding new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'email', 'phone_number')
        }),
    )


# User Profile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Display fields in admin list view
    list_display = ['user', 'website']
    search_fields = ['user__username', 'user__email', 'website']
    list_filter = ['user__user_type']