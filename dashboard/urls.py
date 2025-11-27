from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='overview'),
    path('overview/', views.dashboard_overview, name='overview'),
    path('analytics/', views.dashboard_analytics, name='analytics'),
    path('simple/', views.dashboard_simple, name='simple'),
    path('update-preferences/', views.update_dashboard_preferences, name='update_preferences'),
    path('stats/', views.get_dashboard_stats, name='get_stats'),
]