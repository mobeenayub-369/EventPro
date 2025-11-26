from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event listing and detail pages
    path('', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),

    # Event management (CRUD operations)
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:pk>/delete/', views.delete_event, name='delete_event'),

    # User-specific pages
    path('my-events/', views.my_events, name='my_events'),

    # API endpoints for AJAX (if needed in future)
    # path('api/events/', views.event_list_api, name='event_list_api'),
    # path('api/events/<int:pk>/', views.event_detail_api, name='event_detail_api'),
]

# URL Patterns Explanation:
"""
/events/                    - List all events with filters (event_list)
/events/1/                  - Event detail page (event_detail)
/events/create/             - Create new event (create_event)
/events/1/edit/             - Edit existing event (edit_event)
/events/1/delete/           - Delete event (delete_event)
/events/my-events/          - User's events dashboard (my_events)
"""