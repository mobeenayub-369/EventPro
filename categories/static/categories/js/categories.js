/**
 * Categories App JavaScript
 * Handles interactive functionality for categories features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize categories functionality
    initCategories();
    
    // Initialize event filters if on category detail page
    if (document.querySelector('.category-events-grid')) {
        initEventFilters();
    }
});

/**
 * Initialize categories page functionality
 */
function initCategories() {
    // Category card hover effects
    const categoryCards = document.querySelectorAll('.category-card');
    
    categoryCards.forEach(card => {
        // Add click animation
        card.addEventListener('click', function() {
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
        
        // Add keyboard navigation
        card.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                this.click();
            }
        });
    });
    
    // Category search functionality
    const categorySearch = document.getElementById('categorySearch');
    if (categorySearch) {
        categorySearch.addEventListener('input', filterCategories);
    }
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        const tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Filter categories based on search input
 */
function filterCategories() {
    const searchTerm = this.value.toLowerCase();
    const categories = document.querySelectorAll('.category-card');
    let visibleCount = 0;
    
    categories.forEach(category => {
        const categoryName = category.querySelector('.card-title').textContent.toLowerCase();
        const categoryDesc = category.querySelector('.card-text').textContent.toLowerCase();
        
        if (categoryName.includes(searchTerm) || categoryDesc.includes(searchTerm)) {
            category.style.display = 'block';
            visibleCount++;
        } else {
            category.style.display = 'none';
        }
    });
    
    // Show/hide no results message
    const noResults = document.getElementById('noResults');
    if (noResults) {
        noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
}

/**
 * Initialize event filters for category detail page
 */
function initEventFilters() {
    const filterButtons = document.querySelectorAll('.event-filter-btn');
    const eventCards = document.querySelectorAll('.event-card-category');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter events
            eventCards.forEach(card => {
                if (filter === 'all' || card.getAttribute('data-event-type') === filter) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Load more events functionality (for pagination)
 */
function loadMoreEvents() {
    const loadMoreBtn = document.getElementById('loadMoreEvents');
    const eventsContainer = document.getElementById('eventsContainer');
    
    if (loadMoreBtn && eventsContainer) {
        loadMoreBtn.addEventListener('click', function() {
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Loading...';
            this.disabled = true;
            
            // Simulate API call - Replace with actual implementation
            setTimeout(() => {
                // This would typically make an AJAX call to load more events
                console.log('Loading more events...');
                
                // Reset button state
                this.innerHTML = 'Load More Events';
                this.disabled = false;
            }, 1000);
        });
    }
}

/**
 * Share category functionality
 */
function shareCategory(categorySlug) {
    const shareUrl = `${window.location.origin}/categories/${categorySlug}/`;
    
    if (navigator.share) {
        // Web Share API
        navigator.share({
            title: document.title,
            url: shareUrl
        });
    } else if (navigator.clipboard) {
        // Fallback: Copy to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('Category link copied to clipboard!');
        });
    } else {
        // Final fallback
        prompt('Copy this link:', shareUrl);
    }
}

/**
 * Toggle category favorite status
 */
function toggleFavorite(categoryId) {
    // This would typically make an AJAX call to update favorite status
    const favoriteBtn = document.querySelector(`[data-category-id="${categoryId}"]`);
    
    if (favoriteBtn) {
        const isFavorited = favoriteBtn.classList.contains('favorited');
        
        // Toggle visual state
        favoriteBtn.classList.toggle('favorited');
        favoriteBtn.classList.toggle('text-danger');
        
        // Update icon
        const icon = favoriteBtn.querySelector('i');
        if (icon) {
            icon.className = isFavorited ? 'far fa-heart' : 'fas fa-heart';
        }
        
        // Here you would typically make an API call to save the favorite status
        console.log(`Category ${categoryId} ${isFavorited ? 'removed from' : 'added to'} favorites`);
    }
}

// Export functions for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initCategories,
        filterCategories,
        initEventFilters,
        loadMoreEvents,
        shareCategory,
        toggleFavorite
    };
}