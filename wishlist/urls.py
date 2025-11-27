from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_view, name='wishlist_view'),
    path('add/<int:event_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:event_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('toggle/<int:event_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('clear/', views.clear_wishlist, name='clear_wishlist'),
    path('share/', views.share_wishlist, name='share_wishlist'),
    path('shared/<str:share_token>/', views.shared_wishlist, name='shared_wishlist'),
    path('notifications/', views.wishlist_notifications, name='wishlist_notifications'),
    path('count/', views.get_wishlist_count, name='get_wishlist_count'),
]