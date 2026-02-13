/**
 * API Client for Retail Platform
 * Подключение к backend: https://retail-platform-backend.onrender.com
 */

const API_BASE_URL = 'https://retail-platform-backend.onrender.com/api';

/**
 * API Client - основной класс для работы с API
 */
class ApiClient {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    /**
     * Получить заголовки для запросов
     */
    getHeaders(includeAuth = true) {
        const headers = {
            'Content-Type': 'application/json',
        };

        if (includeAuth && this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        return headers;
    }

    /**
     * Выполнить запрос с обработкой ошибок
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const includeAuth = options.auth !== false;

        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    ...this.getHeaders(includeAuth),
                    ...options.headers,
                },
            });

            // Обработка 401 Unauthorized - пробуем обновить токен
            if (response.status === 401 && includeAuth) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Повторяем запрос с новым токеном
                    return this.request(endpoint, options);
                }
            }

            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.detail || error.message || 'Ошибка запроса');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * GET запрос
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }

    /**
     * POST запрос
     */
    async post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PUT запрос
     */
    async put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE запрос
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }

    /**
     * Обновление access токена
     */
    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.logout();
            return false;
        }

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh_token: this.refreshToken }),
            });

            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }

            const data = await response.json();
            this.setTokens(data.access_token, data.refresh_token || this.refreshToken);
            return true;
        } catch (error) {
            console.error('Token refresh failed:', error);
            this.logout();
            return false;
        }
    }

    /**
     * Сохранить токены
     */
    setTokens(access, refresh) {
        this.accessToken = access;
        this.refreshToken = refresh;
        localStorage.setItem('access_token', access);
        if (refresh) {
            localStorage.setItem('refresh_token', refresh);
        }
    }

    /**
     * Очистить токены и выйти
     */
    logout() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        if (window.location.pathname !== '/auth.html') {
            window.location.href = '/auth.html';
        }
    }

    /**
     * Проверить авторизацию
     */
    isAuthenticated() {
        return !!this.accessToken;
    }

    // ============================================
    // AUTH METHODS
    // ============================================

    async register(data) {
        const response = await this.post('/auth/register', data, { auth: false });
        this.setTokens(response.tokens.access_token, response.tokens.refresh_token);
        localStorage.setItem('user', JSON.stringify(response));
        return response;
    }

    async login(email, password) {
        const response = await this.post('/auth/login', { email, password }, { auth: false });
        // Login endpoint возвращает токены напрямую (без свойства tokens)
        this.setTokens(response.access_token, response.refresh_token);
        // Сохраняем минимальный объект пользователя
        const userObj = { email, tokens: response };
        localStorage.setItem('user', JSON.stringify(userObj));
        return userObj;
    }

    async logoutApi() {
        try {
            await this.post('/auth/logout', {});
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.logout();
        }
    }

    async getCurrentUser() {
        return this.get('/auth/me');
    }

    // ============================================
    // PRODUCTS METHODS
    // ============================================

    async getProducts(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/products${queryString ? `?${queryString}` : ''}`, { auth: false });
    }

    async getProduct(id) {
        return this.get(`/products/${id}`, { auth: false });
    }

    async getCategories() {
        return this.get('/products/categories/list', { auth: false });
    }

    // ============================================
    // CART METHODS
    // ============================================

    async getCart() {
        return this.get('/cart');
    }

    async addToCart(productId, quantity = 1) {
        return this.post('/cart/items', { product_id: productId, quantity });
    }

    async updateCartItem(itemId, quantity) {
        return this.put(`/cart/items/${itemId}`, { quantity });
    }

    async removeFromCart(itemId) {
        return this.delete(`/cart/items/${itemId}`);
    }

    async clearCart() {
        return this.delete('/cart');
    }

    async checkout(orderData) {
        return this.post('/cart/checkout', orderData);
    }

    // ============================================
    // ORDERS METHODS
    // ============================================

    async getOrders(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.get(`/orders${queryString ? `?${queryString}` : ''}`);
    }

    async getOrder(id) {
        return this.get(`/orders/${id}`);
    }

    async cancelOrder(id) {
        return this.post(`/orders/${id}/cancel`, {});
    }
}

// Создаем глобальный экземпляр API клиента
const api = new ApiClient();

// Экспорт для использования в других модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
}
