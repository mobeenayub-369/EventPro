from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('<slug:slug>/', views.event_detail, name='event_detail'),
    path('<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('<slug:slug>/delete/', views.delete_event, name='delete_event'),

    # IMAGE UPLOAD: New route for adding media images
    path('<slug:slug>/add-images/', views.add_event_images, name='add_event_images'),
]