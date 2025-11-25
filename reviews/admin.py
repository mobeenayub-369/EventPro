from django.contrib import admin
from .models import Review, ReviewResponse, ReviewReport


# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'event', 'rating', 'title', 'is_verified',
                    'is_approved', 'has_images', 'created_at', 'get_star_rating']
    list_filter = ['rating', 'is_verified', 'is_approved', 'review_type', 'created_at']
    search_fields = ['user__username', 'event__title', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at', 'has_images']
    list_editable = ['is_approved']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'event', 'rating', 'review_type')
        }),
        ('Review Content', {
            'fields': ('title', 'comment', 'reviewed_at')
        }),
        ('Review Images', {
            'fields': ('image_1', 'image_2', 'image_3'),
            'classes': ('collapse',)
        }),
        ('Review Status', {
            'fields': ('is_verified', 'is_approved', 'is_edited')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
    )

    # Action to approve/reject reviews
    actions = ['approve_reviews', 'reject_reviews', 'verify_reviews']

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')

    approve_reviews.short_description = "Approve selected reviews"

    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews rejected.')

    reject_reviews.short_description = "Reject selected reviews"

    def verify_reviews(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} reviews marked as verified.')

    verify_reviews.short_description = "Mark selected reviews as verified"

    # Display star rating in list
    def get_star_rating(self, obj):
        return obj.get_star_rating()

    get_star_rating.short_description = 'Rating'

    # Display if review has images
    def has_images(self, obj):
        return obj.has_images()

    has_images.boolean = True
    has_images.short_description = 'Has Images'


# Review Response Admin
@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'organizer', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__title', 'organizer__username', 'response_text']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Response Information', {
            'fields': ('review', 'organizer', 'response_text')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Review Report Admin
@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['review__title', 'reporter__username', 'description']
    readonly_fields = ['created_at']
    list_editable = ['status']

    fieldsets = (
        ('Report Information', {
            'fields': ('review', 'reporter', 'reason', 'description')
        }),
        ('Report Status', {
            'fields': ('status', 'resolved_by', 'resolved_at')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    # Action to resolve reports
    actions = ['resolve_reports', 'dismiss_reports']

    def resolve_reports(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_by=request.user, resolved_at=timezone.now())
        self.message_user(request, f'{updated} reports resolved.')

    resolve_reports.short_description = "Mark selected reports as resolved"

    def dismiss_reports(self, request, queryset):
        updated = queryset.update(status='dismissed')
        self.message_user(request, f'{updated} reports dismissed.')

    dismiss_reports.short_description = "Dismiss selected reports"