/**
 * Utilities - Вспомогательные функции
 */

// ============================================
// FORMATTING
// ============================================

const Utils = {
    /**
     * Format price to currency string
     */
    formatPrice(price) {
        const num = parseFloat(price) || 0;
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(num);
    },

    /**
     * Format date to locale string
     */
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },

    /**
     * Format date short (only date)
     */
    formatDateShort(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(date);
    },

    /**
     * Get order status badge class
     */
    getStatusClass(status) {
        const statusClasses = {
            'pending': 'status-pending',
            'confirmed': 'status-confirmed',
            'processing': 'status-processing',
            'shipped': 'status-shipped',
            'delivered': 'status-delivered',
            'cancelled': 'status-cancelled'
        };
        return statusClasses[status] || 'status-pending';
    },

    /**
     * Get order status text in Russian
     */
    getStatusText(status) {
        const statusTexts = {
            'pending': 'Ожидает',
            'confirmed': 'Подтвержден',
            'processing': 'В обработке',
            'shipped': 'Отправлен',
            'delivered': 'Доставлен',
            'cancelled': 'Отменен'
        };
        return statusTexts[status] || status;
    },

    /**
     * Pluralize word in Russian
     */
    pluralize(count, one, few, many) {
        const mod10 = count % 10;
        const mod100 = count % 100;

        if (mod100 >= 11 && mod100 <= 19) {
            return many;
        }
        if (mod10 === 1) {
            return one;
        }
        if (mod10 >= 2 && mod10 <= 4) {
            return few;
        }
        return many;
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * Truncate text
     */
    truncate(text, maxLength = 100) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    },

    /**
     * Generate unique ID
     */
    generateId() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    }
};

// ============================================
// UI HELPERS
// ============================================

const UI = {
    /**
     * Show loading spinner
     */
    showLoading(container) {
        const loadingHtml = `
            <div class="loading-overlay" id="loading-overlay">
                <div class="loading-spinner"></div>
                <p class="loading-text">Загрузка...</p>
            </div>
        `;

        if (typeof container === 'string') {
            container = document.querySelector(container);
        }

        if (container) {
            container.insertAdjacentHTML('beforeend', loadingHtml);
        }
    },

    /**
     * Hide loading spinner
     */
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        // Remove existing toasts
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <span class="toast-message">${Utils.escapeHtml(message)}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
        `;

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('toast-fade-out');
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    },

    /**
     * Show success toast
     */
    success(message) {
        this.showToast(message, 'success');
    },

    /**
     * Show error toast
     */
    error(message) {
        this.showToast(message, 'error');
    },

    /**
     * Show warning toast
     */
    warning(message) {
        this.showToast(message, 'warning');
    },

    /**
     * Show confirm dialog
     */
    confirm(message, onConfirm, onCancel = null) {
        const existingModal = document.querySelector('.confirm-modal');
        if (existingModal) {
            existingModal.remove();
        }

        const modal = document.createElement('div');
        modal.className = 'confirm-modal';
        modal.innerHTML = `
            <div class="confirm-modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="confirm-modal-content">
                <p class="confirm-modal-message">${Utils.escapeHtml(message)}</p>
                <div class="confirm-modal-actions">
                    <button class="btn btn-secondary confirm-cancel">Отмена</button>
                    <button class="btn btn-danger confirm-ok">Подтвердить</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const closeModal = () => modal.remove();

        modal.querySelector('.confirm-cancel').addEventListener('click', () => {
            closeModal();
            if (onCancel) onCancel();
        });

        modal.querySelector('.confirm-ok').addEventListener('click', () => {
            closeModal();
            if (onConfirm) onConfirm();
        });
    },

    /**
     * Update cart badge in header
     */
    async updateCartBadge() {
        const badge = document.querySelector('.cart-badge');
        if (!badge) return;

        if (!TokenManager.isAuthenticated()) {
            badge.style.display = 'none';
            return;
        }

        try {
            const cart = await APIService.cart.get();
            const count = cart.items_count || 0;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        } catch (error) {
            badge.style.display = 'none';
        }
    },

    /**
     * Update user menu in header
     */
    updateUserMenu() {
        const userMenu = document.querySelector('.user-menu');
        if (!userMenu) return;

        if (TokenManager.isAuthenticated()) {
            const user = JSON.parse(localStorage.getItem('user') || '{}');
            const displayName = user.profile?.full_name || user.email || 'Пользователь';

            userMenu.innerHTML = `
                <div class="user-dropdown">
                    <button class="user-dropdown-toggle">
                        <span class="user-avatar">${(displayName[0] || 'U').toUpperCase()}</span>
                        <span class="user-name">${Utils.escapeHtml(displayName)}</span>
                        <span class="dropdown-arrow">▼</span>
                    </button>
                    <div class="dropdown-menu">
                        <a href="orders.html" class="dropdown-item">Мои заказы</a>
                        <a href="profile.html" class="dropdown-item">Профиль</a>
                        <hr class="dropdown-divider">
                        <button class="dropdown-item logout-btn" onclick="Auth.logout()">Выйти</button>
                    </div>
                </div>
            `;
        } else {
            userMenu.innerHTML = `
                <a href="login.html" class="btn btn-outline">Войти</a>
                <a href="register.html" class="btn btn-primary">Регистрация</a>
            `;
        }
    }
};

// ============================================
// FORM HELPERS
// ============================================

const FormHelpers = {
    /**
     * Get form data as object
     */
    getFormData(form) {
        const formData = new FormData(form);
        const data = {};
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    },

    /**
     * Validate email format
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    /**
     * Validate password strength
     */
    isValidPassword(password) {
        return password && password.length >= 8;
    },

    /**
     * Show field error
     */
    showFieldError(field, message) {
        const input = typeof field === 'string' ? document.querySelector(field) : field;
        if (!input) return;

        input.classList.add('input-error');

        // Remove existing error message
        const existingError = input.parentElement.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // Add error message
        const errorEl = document.createElement('span');
        errorEl.className = 'field-error';
        errorEl.textContent = message;
        input.parentElement.appendChild(errorEl);
    },

    /**
     * Clear field error
     */
    clearFieldError(field) {
        const input = typeof field === 'string' ? document.querySelector(field) : field;
        if (!input) return;

        input.classList.remove('input-error');
        const errorEl = input.parentElement.querySelector('.field-error');
        if (errorEl) {
            errorEl.remove();
        }
    },

    /**
     * Clear all form errors
     */
    clearFormErrors(form) {
        const inputs = form.querySelectorAll('.input-error');
        inputs.forEach(input => input.classList.remove('input-error'));

        const errors = form.querySelectorAll('.field-error');
        errors.forEach(error => error.remove());
    }
};

// ============================================
// URL HELPERS
// ============================================

const URLHelpers = {
    /**
     * Get query params from URL
     */
    getQueryParams() {
        const params = new URLSearchParams(window.location.search);
        const result = {};
        for (const [key, value] of params.entries()) {
            result[key] = value;
        }
        return result;
    },

    /**
     * Get single query param
     */
    getQueryParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    },

    /**
     * Update query params
     */
    setQueryParam(name, value) {
        const url = new URL(window.location);
        if (value === null || value === undefined || value === '') {
            url.searchParams.delete(name);
        } else {
            url.searchParams.set(name, value);
        }
        window.history.pushState({}, '', url);
    },

    /**
     * Update multiple query params
     */
    setQueryParams(params) {
        const url = new URL(window.location);
        for (const [key, value] of Object.entries(params)) {
            if (value === null || value === undefined || value === '') {
                url.searchParams.delete(key);
            } else {
                url.searchParams.set(key, value);
            }
        }
        window.history.pushState({}, '', url);
    }
};

// Export
window.Utils = Utils;
window.UI = UI;
window.FormHelpers = FormHelpers;
window.URLHelpers = URLHelpers;
