from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Conversation management
    path('', views.inbox, name='inbox'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('new/<int:user_id>/', views.new_conversation, name='new_conversation_user'),
    path('thread/<int:conversation_id>/', views.thread_detail, name='thread_detail'),
    path('thread/<int:conversation_id>/archive/', views.archive_conversation, name='archive_conversation'),
    path('thread/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),

    # Message interactions
    path('search/', views.search_messages, name='search_messages'),
    path('settings/', views.message_settings, name='message_settings'),
    path('block/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),

    # AJAX endpoints
    path('ajax/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('ajax/message/<int:message_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
]