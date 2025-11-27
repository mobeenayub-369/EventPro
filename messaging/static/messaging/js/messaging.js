/**
 * Messaging App JavaScript
 * Handles real-time messaging functionality and UI interactions
 */

class MessagingApp {
    constructor() {
        this.currentConversation = null;
        this.autoRefreshInterval = null;
        this.init();
    }

    init() {
        this.initializeEventListeners();
        this.initializeAutoRefresh();
        this.initializeMessageForm();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Message form submission
        const messageForm = document.getElementById('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', this.handleMessageSubmit.bind(this));
        }

        // File attachment preview
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }

        // Real-time message updates
        this.initializeRealTimeUpdates();
    }

    /**
     * Handle message form submission
     */
    async handleMessageSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Show loading state
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Sending...';
        submitButton.disabled = true;
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            if (response.ok) {
                // Success - reload the page to show new message
                window.location.reload();
            } else {
                throw new Error('Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showNotification('Failed to send message. Please try again.', 'error');
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }

    /**
     * Handle file selection for attachments
     */
    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file size (10MB)
            if (file.size > 10 * 1024 * 1024) {
                this.showNotification('File size must be less than 10MB', 'error');
                e.target.value = '';
                return;
            }
            
            // Show file preview
            this.showFilePreview(file);
        }
    }

    /**
     * Show file preview before upload
     */
    showFilePreview(file) {
        // Remove existing preview
        this.removeFilePreview();
        
        const preview = document.createElement('div');
        preview.className = 'file-preview alert alert-info mt-2';
        preview.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file me-2"></i>
                <div class="flex-grow-1">
                    <strong>${file.name}</strong>
                    <div class="small">${this.formatFileSize(file.size)}</div>
                </div>
                <button type="button" class="btn-close" onclick="messagingApp.removeFilePreview()"></button>
            </div>
        `;
        
        const form = document.getElementById('messageForm');
        form.appendChild(preview);
    }

    /**
     * Remove file preview
     */
    removeFilePreview() {
        const existingPreview = document.querySelector('.file-preview');
        if (existingPreview) {
            existingPreview.remove();
        }
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Initialize auto-refresh for new messages
     */
    initializeAutoRefresh() {
        // Only auto-refresh on conversation pages
        if (window.location.pathname.includes('/thread/')) {
            this.autoRefreshInterval = setInterval(() => {
                this.checkForNewMessages();
            }, 10000); // Check every 10 seconds
        }
    }

    /**
     * Check for new messages
     */
    async checkForNewMessages() {
        try {
            const response = await fetch(window.location.href, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            if (response.ok) {
                const text = await response.text();
                const parser = new DOMParser();
                const newDoc = parser.parseFromString(text, 'text/html');
                
                // Compare message counts or timestamps to detect new messages
                this.updateMessageDisplay(newDoc);
            }
        } catch (error) {
            console.error('Error checking for new messages:', error);
        }
    }

    /**
     * Update message display with new messages
     */
    updateMessageDisplay(newDoc) {
        const currentMessages = document.querySelectorAll('.message-item');
        const newMessages = newDoc.querySelectorAll('.message-item');
        
        if (newMessages.length > currentMessages.length) {
            // New messages detected - you could implement a more sophisticated update
            console.log('New messages available');
            // In a real implementation, you would update the UI with new messages
        }
    }

    /**
     * Initialize real-time updates (WebSocket or polling)
     */
    initializeRealTimeUpdates() {
        // This would be implemented with WebSockets in a production environment
        console.log('Real-time messaging initialized');
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        // Add to toast container
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
        bsToast.show();
        
        // Remove after hide
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Get appropriate icon for notification type
     */
    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Cleanup when leaving page
     */
    destroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }
}

// Initialize messaging app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.messagingApp = new MessagingApp();
});

// Cleanup when leaving page
window.addEventListener('beforeunload', function() {
    if (window.messagingApp) {
        window.messagingApp.destroy();
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MessagingApp;
}