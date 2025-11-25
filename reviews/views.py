from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator

from .models import Review, ReviewResponse, ReviewReport
from .forms import ReviewForm, ReviewEditForm, ReviewResponseForm, ReviewReportForm
from events.models import Event
from bookings.models import Booking


# Review List View (Home page for reviews)
def review_list(request):
    """
    Home page for reviews - shows all approved reviews
    """
    # Get all approved reviews with related data
    reviews = Review.objects.filter(
        is_approved=True
    ).select_related('user', 'event').prefetch_related('response').order_by('-created_at')

    # Calculate overall statistics
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'reviews': page_reviews,
        'stats': stats,
        'title': 'All Reviews'
    }
    return render(request, 'reviews/review_list.html', context)


# Create Review View
@login_required
def create_review(request, event_slug):
    # Get event object
    event = get_object_or_404(Event, slug=event_slug, is_active=True)

    # Check if user has attended the event
    has_attended = Booking.objects.filter(
        user=request.user,
        event=event,
        status='confirmed'
    ).exists()

    # Check if user already reviewed this event
    existing_review = Review.objects.filter(user=request.user, event=event).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this event.')
        return redirect('review_detail', review_id=existing_review.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)  # Added request.FILES for image upload
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.event = event
            review.is_verified = has_attended  # Auto-verify if user attended
            review.save()

            messages.success(request, 'Thank you for your review! Your images have been uploaded successfully.')
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'event': event,
        'has_attended': has_attended,
        'title': f'Review {event.title}'
    }
    return render(request, 'reviews/create_review.html', context)


# Event Reviews List View
def event_reviews(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug, is_active=True)

    # Get approved reviews for this event
    reviews = Review.objects.filter(
        event=event,
        is_approved=True
    ).select_related('user').prefetch_related('response')

    # Calculate rating statistics
    rating_stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    # Get rating distribution
    rating_distribution = {}
    for rating in range(1, 6):
        rating_distribution[rating] = reviews.filter(rating=rating).count()

    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'event': event,
        'reviews': page_reviews,
        'rating_stats': rating_stats,
        'rating_distribution': rating_distribution,
        'title': f'Reviews for {event.title}'
    }
    return render(request, 'reviews/event_reviews.html', context)


# My Reviews View
@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related('event').order_by('-created_at')

    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'reviews': page_reviews,
        'title': 'My Reviews'
    }
    return render(request, 'reviews/my_reviews.html', context)


# Review Detail View
def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id, is_approved=True)

    # Get review images
    review_images = review.get_review_images()

    context = {
        'review': review,
        'review_images': review_images,
        'title': f'Review by {review.user.username}'
    }
    return render(request, 'reviews/review_detail.html', context)


# Edit Review View
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    # Check if review can be edited
    if not review.can_edit():
        messages.error(request, 'This review can no longer be edited.')
        return redirect('review_detail', review_id=review.id)

    if request.method == 'POST':
        form = ReviewEditForm(request.POST, request.FILES, instance=review)  # Added request.FILES
        if form.is_valid():
            review = form.save(commit=False)
            review.is_edited = True
            review.save()

            messages.success(request, 'Review updated successfully!')
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewEditForm(instance=review)

    # Get current review images
    review_images = review.get_review_images()

    context = {
        'form': form,
        'review': review,
        'review_images': review_images,
        'title': 'Edit Review'
    }
    return render(request, 'reviews/edit_review.html', context)


# Delete Review View
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        event_slug = review.event.slug
        review.delete()

        messages.success(request, 'Review deleted successfully!')
        return redirect('event_reviews', event_slug=event_slug)

    context = {
        'review': review,
        'title': 'Delete Review'
    }
    return render(request, 'reviews/delete_review.html', context)


# Delete Review Image View
@login_required
def delete_review_image(request, review_id, image_field):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    # Check if review can be edited
    if not review.can_edit():
        messages.error(request, 'This review can no longer be edited.')
        return redirect('review_detail', review_id=review.id)

    # Delete the specified image
    if image_field == 'image_1':
        review.image_1.delete(save=True)
    elif image_field == 'image_2':
        review.image_2.delete(save=True)
    elif image_field == 'image_3':
        review.image_3.delete(save=True)

    messages.success(request, 'Image deleted successfully!')
    return redirect('edit_review', review_id=review.id)


# Create Review Response View (Organizer)
@login_required
def create_response(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Check if user is the event organizer
    if review.event.organizer != request.user:
        messages.error(request, 'You can only respond to reviews for your own events.')
        return redirect('review_detail', review_id=review.id)

    # Check if response already exists
    if hasattr(review, 'response'):
        messages.info(request, 'You have already responded to this review.')
        return redirect('review_detail', review_id=review.id)

    if request.method == 'POST':
        form = ReviewResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.organizer = request.user
            response.save()

            messages.success(request, 'Response added successfully!')
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewResponseForm()

    context = {
        'form': form,
        'review': review,
        'title': 'Respond to Review'
    }
    return render(request, 'reviews/create_response.html', context)


# Edit Review Response View (Organizer)
@login_required
def edit_response(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Check if user is the event organizer
    if review.event.organizer != request.user:
        messages.error(request, 'You can only edit responses for your own events.')
        return redirect('review_detail', review_id=review.id)

    # Check if response exists
    try:
        response = ReviewResponse.objects.get(review=review)
    except ReviewResponse.DoesNotExist:
        messages.error(request, 'No response found to edit.')
        return redirect('review_detail', review_id=review.id)

    if request.method == 'POST':
        form = ReviewResponseForm(request.POST, instance=response)
        if form.is_valid():
            form.save()
            messages.success(request, 'Response updated successfully!')
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewResponseForm(instance=response)

    context = {
        'form': form,
        'review': review,
        'response': response,
        'title': 'Edit Response'
    }
    return render(request, 'reviews/edit_response.html', context)


# Delete Review Response View (Organizer)
@login_required
def delete_response(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Check if user is the event organizer
    if review.event.organizer != request.user:
        messages.error(request, 'You can only delete responses for your own events.')
        return redirect('review_detail', review_id=review.id)

    # Check if response exists
    try:
        response = ReviewResponse.objects.get(review=review)
    except ReviewResponse.DoesNotExist:
        messages.error(request, 'No response found to delete.')
        return redirect('review_detail', review_id=review.id)

    if request.method == 'POST':
        response.delete()
        messages.success(request, 'Response deleted successfully!')
        return redirect('review_detail', review_id=review.id)

    context = {
        'review': review,
        'response': response,
        'title': 'Delete Response'
    }
    return render(request, 'reviews/delete_response.html', context)


# Report Review View
@login_required
def report_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, is_approved=True)

    # Check if user already reported this review
    existing_report = ReviewReport.objects.filter(review=review, reporter=request.user).first()
    if existing_report:
        messages.info(request, 'You have already reported this review.')
        return redirect('review_detail', review_id=review.id)

    if request.method == 'POST':
        form = ReviewReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.review = review
            report.reporter = request.user
            report.save()

            messages.success(request, 'Thank you for reporting this review. We will investigate it.')
            return redirect('review_detail', review_id=review.id)
    else:
        form = ReviewReportForm()

    context = {
        'form': form,
        'review': review,
        'title': 'Report Review'
    }
    return render(request, 'reviews/report_review.html', context)


# Review Reports View (For organizers/admin to see reported reviews)
@login_required
def review_reports(request):
    """
    View for organizers and admin to see reported reviews
    """
    # Check if user is staff or organizer
    if request.user.is_staff:
        # Admin can see all reports
        reports = ReviewReport.objects.all()
    else:
        # Organizer can only see reports for their events
        organized_events = Event.objects.filter(organizer=request.user)
        reports = ReviewReport.objects.filter(review__event__in=organized_events)

    reports = reports.select_related(
        'review',
        'reporter',
        'review__event',
        'review__user'
    ).order_by('-created_at', '-resolved')

    # Count statistics
    total_reports = reports.count()
    resolved_reports = reports.filter(resolved=True).count()
    pending_reports = reports.filter(resolved=False).count()

    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_reports = paginator.get_page(page_number)

    context = {
        'reports': page_reports,
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'pending_reports': pending_reports,
        'title': 'Review Reports'
    }
    return render(request, 'reviews/review_reports.html', context)


# Organizer Reviews View
@login_required
def organizer_reviews(request):
    # Get events organized by the user
    organized_events = Event.objects.filter(organizer=request.user, is_active=True)

    # Get reviews for these events
    reviews = Review.objects.filter(
        event__in=organized_events,
        is_approved=True
    ).select_related('user', 'event').prefetch_related('response').order_by('-created_at')

    # Calculate organizer rating statistics
    org_rating_stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'reviews': page_reviews,
        'org_rating_stats': org_rating_stats,
        'title': 'Event Reviews'
    }
    return render(request, 'reviews/organizer_reviews.html', context)