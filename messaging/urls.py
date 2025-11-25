from django.urls import path
from webcolors import names

from . import views

urlpatterns= [
    path('', views.inbox, name='inbox'),
    path('thread/<int:thread_id>', views.thread_detail, name='thread_detail'),
    path('start/<int:user_id>', views.start_thread, name='start_thread'),
    path('api/thread/<int:thread_id>/send/', views.send_message_api, name='send_message_api'),
    path('api/unread-count', views.get_unread_count, name='get_unread_count'),
]