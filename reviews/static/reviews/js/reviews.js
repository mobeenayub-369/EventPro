/**
 * Reviews App JavaScript
 * Handles interactive functionality for Fiverr-style review system
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeReviewsApp();
});

/**
 * Initialize all reviews functionality
 */
function initializeReviewsApp() {
    initializeHelpfulButtons();
    initializeRatingSelection();
    initializeReviewFilters();
    initializeReviewSearch();
}

/**
 * Initialize helpful vote buttons with AJAX functionality
 */
function initializeHelpfulButtons() {
    const helpfulButtons = document.querySelectorAll('.helpful-btn');
    
    helpfulButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const reviewId = this.getAttribute('data-review-id');
            const isHelpful = this.getAttribute('data-helpful') === 'true';
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Voting...';
            this.disabled = true;
            
            // Send AJAX request
            voteReview(reviewId, isHelpful)
                .then(data => {
                    if (data.success) {
                        // Update button state
                        this.classList.add('voted');
                        this.innerHTML = `<i class="fas fa-thumbs-up me-1"></i> Helpful (${data.helpful_count})`;
                        
                        // Update all buttons for this review
                        updateAllHelpfulButtons(reviewId, data.helpful_count, data.user_vote);
                        
                        // Show success message
                        showToast('Thanks for your feedback!', 'success');
                    } else {
                        showToast('Failed to submit vote. Please try again.', 'error');
                        this.innerHTML = originalText;
                    }
                })
                .catch(error => {
                    console.error('Error voting:', error);
                    showToast('An error occurred. Please try again.', 'error');
                    this.innerHTML = originalText;
                })
                .finally(() => {
                    this.disabled = false;
                });
        });
    });
}

/**
 * Send AJAX request to vote on a review
 */
async function voteReview(reviewId, isHelpful) {
    const formData = new FormData();
    formData.append('helpful', isHelpful);
    
    const response = await fetch(`/reviews/${reviewId}/vote/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken(),
        },
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    
    return await response.json();
}

/**
 * Update all helpful buttons for a specific review
 */
function updateAllHelpfulButtons(reviewId, helpfulCount, userVote) {
    const allButtons = document.querySelectorAll(`.helpful-btn[data-review-id="${reviewId}"]`);
    
    allButtons.forEach(button => {
        // Update count
        const countBadge = button.querySelector('.badge');
        if (countBadge) {
            countBadge.textContent = helpfulCount;
        } else {
            // Update text content
            button.innerHTML = button.innerHTML.replace(/\(\d+\)/, `(${helpfulCount})`);
        }
        
        // Update visual state
        if (userVote) {
            button.classList.add('voted');
            button.setAttribute('data-helpful', 'true');
        } else {
            button.classList.remove('voted');
            button.setAttribute('data-helpful', 'false');
        }
    });
}

/**
 * Initialize rating selection with enhanced UI
 */
function initializeRatingSelection() {
    const ratingInputs = document.querySelectorAll('input[name="rating"]');
    
    ratingInputs.forEach(input => {
        // Set initial state
        updateRatingLabel(input);
        
        // Add change listener
        input.addEventListener('change', function() {
            updateRatingLabel(this);
            validateReviewForm();
        });
    });
}

/**
 * Update rating label appearance based on selection
 */
function updateRatingLabel(input) {
    const label = input.nextElementSibling;
    const stars = label.querySelector('.stars, .stars-edit');
    
    if (input.checked) {
        label.classList.add('selected');
        stars.classList.add('selected');
    } else {
        label.classList.remove('selected');
        stars.classList.remove('selected');
    }
}

/**
 * Initialize review filtering functionality
 */
function initializeReviewFilters() {
    const filterForm = document.getElementById('reviewFilterForm');
    if (filterForm) {
        // Auto-submit on some filter changes
        const autoSubmitElements = filterForm.querySelectorAll('select, input[type="checkbox"]');
        autoSubmitElements.forEach(element => {
            element.addEventListener('change', function() {
                // Small delay to allow multiple selections
                setTimeout(() => {
                    filterForm.submit();
                }, 300);
            });
        });
    }
}

/**
 * Initialize review search functionality
 */
function initializeReviewSearch() {
    const searchInput = document.getElementById('reviewSearch');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                searchReviews(this.value);
            }, 500);
        });
    }
}

/**
 * Search reviews (client-side filtering)
 */
function searchReviews(query) {
    const reviewCards = document.querySelectorAll('.review-card');
    const noResults = document.getElementById('noResults');
    let visibleCount = 0;
    
    reviewCards.forEach(card => {
        const reviewText = card.textContent.toLowerCase();
        if (reviewText.includes(query.toLowerCase())) {
            card.style.display = 'block';
            visibleCount++;
            
            // Highlight matching text
            highlightText(card, query);
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide no results message
    if (noResults) {
        noResults.classList.toggle('d-none', visibleCount > 0);
        noResults.classList.toggle('d-block', visibleCount === 0);
    }
}

/**
 * Highlight search terms in review text
 */
function highlightText(element, query) {
    // Remove previous highlights
    const highlights = element.querySelectorAll('.search-highlight');
    highlights.forEach(highlight => {
        const parent = highlight.parentNode;
        parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        parent.normalize();
    });
    
    // Add new highlights
    if (query.trim()) {
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            const text = node.textContent;
            const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
            const newText = text.replace(regex, '<mark class="search-highlight bg-warning">$1</mark>');
            
            if (newText !== text) {
                const newElement = document.createElement('span');
                newElement.innerHTML = newText;
                node.parentNode.replaceChild(newElement, node);
            }
        }
    }
}

/**
 * Escape special characters for regex
 */
function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Validate review form before submission
 */
function validateReviewForm() {
    const form = document.getElementById('reviewForm');
    if (!form) return true;
    
    const rating = form.querySelector('input[name="rating"]:checked');
    const comment = form.querySelector('textarea[name="comment"]');
    
    let isValid = true;
    
    // Validate rating
    if (!rating) {
        showFieldError('Please select a rating', form);
        isValid = false;
    }
    
    // Validate comment length if provided
    if (comment && comment.value.trim().length > 0 && comment.value.trim().length < 10) {
        showFieldError('Comment must be at least 10 characters long', form, comment);
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show field error message
 */
function showFieldError(message, form, element = null) {
    // Remove existing error messages
    const existingErrors = form.querySelectorAll('.field-error');
    existingErrors.forEach(error => error.remove());
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error alert alert-danger mt-2';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
    
    // Insert error message
    if (element) {
        element.parentNode.insertBefore(errorDiv, element.nextSibling);
    } else {
        form.insertBefore(errorDiv, form.firstChild);
    }
    
    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
    bsToast.show();
    
    // Remove toast after hide
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Get appropriate icon for toast type
 */
function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Get CSRF token from cookies
 */
function getCSRFToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Export functions for use in other modules
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeReviewsApp,
        voteReview,
        searchReviews,
        validateReviewForm,
        showToast
    };
}