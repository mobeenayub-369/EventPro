from django.urls import path
from . import views

urlpatterns = [
    # Review URLs
    path('event/<slug:event_slug>/create/', views.create_review, name='create_review'),
    path('event/<slug:event_slug>/', views.event_reviews, name='event_reviews'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('<int:review_id>/delete-image/<str:image_field>/', views.delete_review_image, name='delete_review_image'),
    path('<int:review_id>/', views.review_detail, name='review_detail'),

    # Review Response URLs
    path('<int:review_id>/response/create/', views.create_response, name='create_response'),
    path('<int:review_id>/response/edit/', views.edit_response, name='edit_response'),
    path('<int:review_id>/response/delete/', views.delete_response, name='delete_response'),

    # Review Report URLs
    path('<int:review_id>/report/', views.report_review, name='report_review'),
    path('reports/', views.review_reports, name='review_reports'),

    # Organizer Review Management
    path('organizer/reviews/', views.organizer_reviews, name='organizer_reviews'),
]