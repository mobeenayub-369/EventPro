from django.urls import path
from . import views


urlpatterns = [
    path('', views.notifications_list, name='notifications_list'),
    path('read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('read-all/', views.mark_all_as_read, name='mark_all_as_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('api/unread-count/', views.get_unread_count_api, name='get_unread_count_api'),
]