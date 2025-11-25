from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='categories'),
    path('tags/', views.tag_list, name='tags'),
    path('<slug:category_slug>/', views.category_events, name='category_events'),
    path('tag/<slug:tag_slug>/', views.tag_events, name='tag_events'),
]