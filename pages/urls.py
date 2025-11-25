from django.urls import path
from . import views

urlpatterns = [
    # Public page view
    path('<slug:slug>/', views.page_detail, name='page_detail'),

    # Page management URLs (staff only)
    path('', views.page_list, name='page_list'),
    path('create/', views.create_page, name='create_page'),
    path('<slug:slug>/edit/', views.edit_page, name='edit_page'),
    path('<slug:slug>/delete/', views.delete_page, name='delete_page'),
]