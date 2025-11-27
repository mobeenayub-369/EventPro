from django.urls import path
from . import views

# App name for namespacing URLs (e.g., categories:category_list)
app_name = 'categories'

urlpatterns = [
    # URL pattern for category list page
    path('', views.CategoryListView.as_view(), name='category_list'),

    # URL pattern for individual category detail page using slug
    path('<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
]