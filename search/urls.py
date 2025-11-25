from django.urls import path
from . import views

urlpatterns = [
    # Search URLs
    path('', views.advanced_search, name='advanced_search'),
    path('quick/', views.quick_search, name='quick_search'),
    path('suggestions/', views.search_suggestions, name='search_suggestions'),

    # Filter URLs
    path('category/<slug:category_slug>/', views.category_events, name='category_events'),
    path('tag/<slug:tag_slug>/', views.tag_events, name='tag_events'),
]