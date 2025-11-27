from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_feed, name='list'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
    path('preferences/', views.notification_preferences, name='preferences'),
    path('unread-count/', views.get_unread_count, name='unread_count'),
]