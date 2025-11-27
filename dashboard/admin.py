from django.contrib import admin
from .models import UserDashboard, DashboardWidget, UserActivity, DashboardMetric

@admin.register(UserDashboard)
class UserDashboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'last_visited', 'preferred_view']
    list_filter = ['preferred_view', 'last_visited']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_visited']

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'widget_type', 'title', 'position', 'is_visible']
    list_filter = ['widget_type', 'is_visible', 'created_at']
    search_fields = ['user__username', 'title']
    list_editable = ['position', 'is_visible']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    list_per_page = 20

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ['user', 'metric_type', 'value', 'period', 'recorded_at']
    list_filter = ['metric_type', 'period', 'recorded_at']
    search_fields = ['user__username']
    readonly_fields = ['recorded_at']