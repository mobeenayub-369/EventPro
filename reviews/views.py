from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
from .models import Review, ReviewVote
from events.models import Event
from .forms import ReviewForm, ReviewResponseForm, ReviewFilterForm


@login_required
def create_review(request, event_id):
    """
    Create a new review for an event.
    Similar to Fiverr's review system where users can rate services.
    """
    event = get_object_or_404(Event, id=event_id)

    # Check if user has already reviewed this event
    existing_review = Review.objects.filter(event=event, user=request.user).first()
    if existing_review:
        messages.warning(request, 'You have already submitted a review for this event.')
        return redirect('reviews:event_reviews', event_id=event.id)

    # Check if user can review (should have attended/booking - to be integrated)
    if not event.can_user_review(request.user):
        messages.error(request, 'You need to attend an event to review it.')
        return redirect('events:event_detail', event_id=event.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.event = event
                review.user = request.user
                review.is_verified = True  # Mark as verified if booking exists
                review.save()

                messages.success(request, 'Thank you! Your review has been submitted successfully.')
                return redirect('reviews:event_reviews', event_id=event.id)

            except Exception as e:
                messages.error(request, 'An error occurred while submitting your review. Please try again.')
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'event': event,
        'title': f'Review {event.title}'
    }
    return render(request, 'reviews/create_review.html', context)


def event_reviews(request, event_id):
    """
    Display all reviews for a specific event with filtering and sorting.
    Similar to Fiverr's review section for each gig.
    """
    event = get_object_or_404(Event, id=event_id)

    # Get all reviews for this event
    reviews = Review.objects.filter(event=event).select_related('user')

    # Apply filters and sorting
    filter_form = ReviewFilterForm(request.GET)
    if filter_form.is_valid():
        sort_by = filter_form.cleaned_data.get('sort_by', 'newest')
        min_rating = filter_form.cleaned_data.get('min_rating')
        has_response = filter_form.cleaned_data.get('has_response')

        # Apply rating filter
        if min_rating:
            reviews = reviews.filter(rating__gte=int(min_rating))

        # Apply response filter
        if has_response:
            reviews = reviews.filter(organizer_response__isnull=False)

        # Apply sorting
        if sort_by == 'newest':
            reviews = reviews.order_by('-created_at')
        elif sort_by == 'oldest':
            reviews = reviews.order_by('created_at')
        elif sort_by == 'highest':
            reviews = reviews.order_by('-rating', '-created_at')
        elif sort_by == 'lowest':
            reviews = reviews.order_by('rating', '-created_at')
        elif sort_by == 'most_helpful':
            reviews = reviews.annotate(helpful_count=Count('votes')).order_by('-helpful_count', '-created_at')
    else:
        filter_form = ReviewFilterForm()
        reviews = reviews.order_by('-created_at')  # Default: newest first

    # Calculate review statistics
    review_stats = {
        'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
        'total_reviews': reviews.count(),
        'rating_distribution': reviews.values('rating').annotate(count=Count('id')).order_by('-rating')
    }

    # Pagination
    paginator = Paginator(reviews, 10)  # 10 reviews per page
    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    context = {
        'event': event,
        'reviews': page_reviews,
        'filter_form': filter_form,
        'review_stats': review_stats,
        'title': f'Reviews for {event.title}'
    }
    return render(request, 'reviews/event_reviews.html', context)


@login_required
def edit_review(request, review_id):
    """
    Edit an existing review.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated successfully.')
            return redirect('reviews:event_reviews', event_id=review.event.id)
    else:
        form = ReviewForm(instance=review)

    context = {
        'form': form,
        'review': review,
        'event': review.event,
        'title': 'Edit Review'
    }
    return render(request, 'reviews/edit_review.html', context)


@login_required
def delete_review(request, review_id):
    """
    Delete a review with confirmation.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    event_id = review.event.id

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted successfully.')
        return redirect('reviews:event_reviews', event_id=event_id)

    context = {
        'review': review,
        'event': review.event,
        'title': 'Delete Review'
    }
    return render(request, 'reviews/delete_review.html', context)


@login_required
def my_reviews(request):
    """
    Display all reviews submitted by the current user.
    """
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


@login_required
def organizer_reviews(request):
    """
    Display all reviews for events organized by the current user.
    Similar to Fiverr's seller review management.
    """
    # Get events organized by current user
    organized_events = Event.objects.filter(organizer=request.user)
    reviews = Review.objects.filter(event__in=organized_events).select_related('event', 'user').order_by('-created_at')

    # Calculate organizer statistics
    organizer_stats = {
        'total_reviews': reviews.count(),
        'average_rating': reviews.aggregate(Avg('rating'))['rating__avg'] or 0,
        'events_with_reviews': organized_events.filter(reviews__isnull=False).distinct().count(),
        'pending_responses': reviews.filter(organizer_response='').count()
    }

    context = {
        'reviews': reviews,
        'organizer_stats': organizer_stats,
        'title': 'Reviews for My Events'
    }
    return render(request, 'reviews/organizer_reviews.html', context)


@login_required
def add_review_response(request, review_id):
    """
    Add or update organizer response to a review.
    """
    review = get_object_or_404(Review, id=review_id)

    # Check if current user is the event organizer
    if review.event.organizer != request.user:
        messages.error(request, 'You can only respond to reviews for your own events.')
        return redirect('reviews:event_reviews', event_id=review.event.id)

    if request.method == 'POST':
        form = ReviewResponseForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.add_organizer_response(form.cleaned_data['organizer_response'])
            messages.success(request, 'Your response has been added to the review.')
            return redirect('reviews:event_reviews', event_id=review.event.id)
    else:
        form = ReviewResponseForm(instance=review)

    context = {
        'form': form,
        'review': review,
        'event': review.event,
        'title': 'Respond to Review'
    }
    return render(request, 'reviews/review_response.html', context)


@login_required
def vote_review(request, review_id):
    """
    Handle helpful/not helpful votes for reviews.
    AJAX compatible view.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        review = get_object_or_404(Review, id=review_id)
        is_helpful = request.POST.get('helpful') == 'true'

        # Check if user already voted
        existing_vote = ReviewVote.objects.filter(review=review, user=request.user).first()

        if existing_vote:
            # Update existing vote
            if existing_vote.is_helpful != is_helpful:
                existing_vote.is_helpful = is_helpful
                existing_vote.save()
                # Update helpful count
                review.helpful_count = review.votes.filter(is_helpful=True).count()
                review.save()
        else:
            # Create new vote
            ReviewVote.objects.create(review=review, user=request.user, is_helpful=is_helpful)
            # Update helpful count
            review.helpful_count = review.votes.filter(is_helpful=True).count()
            review.save()

        return JsonResponse({
            'success': True,
            'helpful_count': review.helpful_count,
            'user_vote': is_helpful
        })

    return JsonResponse({'success': False, 'error': 'Invalid request'})


def review_detail(request, review_id):
    """
    Display a single review in detail.
    """
    review = get_object_or_404(Review, id=review_id)

    context = {
        'review': review,
        'event': review.event,
        'title': f'Review by {review.user.username}'
    }
    return render(request, 'reviews/review_detail.html', context)