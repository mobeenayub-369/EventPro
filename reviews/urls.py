from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Review management
    path('event/<int:event_id>/create/', views.create_review, name='create_review'),
    path('event/<int:event_id>/', views.event_reviews, name='event_reviews'),
    path('<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('<int:review_id>/', views.review_detail, name='review_detail'),

    # User reviews
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('organizer-reviews/', views.organizer_reviews, name='organizer_reviews'),

    # Review interactions
    path('<int:review_id>/response/', views.add_review_response, name='add_review_response'),
    path('<int:review_id>/vote/', views.vote_review, name='vote_review'),
]