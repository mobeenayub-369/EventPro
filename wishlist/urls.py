from django.urls import path
from . import views

urlpatterns = [
    path('', views.wishlist_detail, name='wishlist_detail'),
    path('add/<int:event_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('clear/', views.clear_wishlist, name='clear_wishlist'),
    path('toggle/<int:event_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('count/', views.wishlist_count, name='wishlist_count'),
]