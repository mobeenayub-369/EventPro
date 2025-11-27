from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_events, name='search_events'),
    path('suggestions/', views.search_suggestions, name='search_suggestions'),
    path('analytics/', views.search_analytics, name='search_analytics'),
]