/**
 * API Client - Клиент для работы с Backend API
 * Base URL: https://retail-platform-backend.onrender.com
 */

const API_BASE_URL = 'https://retail-platform-backend.onrender.com';

// ============================================
// TOKEN MANAGEMENT
// ============================================

const TokenManager = {
    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    },

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    },

    isAuthenticated() {
        return !!this.getAccessToken();
    }
};

// ============================================
// API CLIENT
// ============================================

class APIClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add auth token if available
        const token = TokenManager.getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            // Handle 401 - try to refresh token
            if (response.status === 401 && TokenManager.getRefreshToken()) {
                const refreshed = await this.refreshAccessToken();
                if (refreshed) {
                    // Retry request with new token
                    headers['Authorization'] = `Bearer ${TokenManager.getAccessToken()}`;
                    const retryResponse = await fetch(url, { ...config, headers });
                    return this.handleResponse(retryResponse);
                } else {
                    // Refresh failed - logout user
                    TokenManager.clearTokens();
                    window.location.href = '/frontend/html/login.html';
                    throw new Error('Session expired');
                }
            }

            return this.handleResponse(response);
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new APIError(
                errorData.detail || `HTTP Error: ${response.status}`,
                response.status,
                errorData
            );
        }

        // Handle empty responses
        const text = await response.text();
        return text ? JSON.parse(text) : null;
    }

    async refreshAccessToken() {
        try {
            const refreshToken = TokenManager.getRefreshToken();
            if (!refreshToken) return false;

            const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                TokenManager.setTokens(data.access_token, data.refresh_token);
                return true;
            }
            return false;
        } catch {
            return false;
        }
    }

    // HTTP Methods
    get(endpoint, params = {}) {
        const queryString = new URLSearchParams(
            Object.entries(params).filter(([_, v]) => v !== null && v !== undefined)
        ).toString();

        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// ============================================
// CUSTOM ERROR CLASS
// ============================================

class APIError extends Error {
    constructor(message, status, data) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

// ============================================
// API SERVICE
// ============================================

const api = new APIClient(API_BASE_URL);

const APIService = {
    // ----------------------------------------
    // AUTH
    // ----------------------------------------
    auth: {
        async register(email, password, firstName = null, lastName = null) {
            const data = await api.post('/api/auth/register', {
                email,
                password,
                first_name: firstName,
                last_name: lastName
            });
            if (data.tokens) {
                TokenManager.setTokens(data.tokens.access_token, data.tokens.refresh_token);
            }
            return data;
        },

        async login(email, password) {
            const data = await api.post('/api/auth/login', { email, password });
            TokenManager.setTokens(data.access_token, data.refresh_token);
            return data;
        },

        async logout() {
            try {
                await api.post('/api/auth/logout');
            } finally {
                TokenManager.clearTokens();
            }
        },

        async getCurrentUser() {
            return api.get('/api/auth/me');
        },

        isAuthenticated() {
            return TokenManager.isAuthenticated();
        }
    },

    // ----------------------------------------
    // PRODUCTS
    // ----------------------------------------
    products: {
        async list(params = {}) {
            return api.get('/api/products', params);
        },

        async get(productId) {
            return api.get(`/api/products/${productId}`);
        },

        async getCategories() {
            return api.get('/api/products/categories/list');
        },

        async create(data) {
            return api.post('/api/products', data);
        },

        async update(productId, data) {
            return api.put(`/api/products/${productId}`, data);
        },

        async delete(productId) {
            return api.delete(`/api/products/${productId}`);
        }
    },

    // ----------------------------------------
    // CART
    // ----------------------------------------
    cart: {
        async get() {
            return api.get('/api/cart');
        },

        async addItem(productId, quantity = 1) {
            return api.post('/api/cart/items', {
                product_id: productId,
                quantity
            });
        },

        async updateItem(itemId, quantity) {
            return api.put(`/api/cart/items/${itemId}`, { quantity });
        },

        async removeItem(itemId) {
            return api.delete(`/api/cart/items/${itemId}`);
        },

        async clear() {
            return api.delete('/api/cart');
        },

        async checkout(shippingAddress) {
            return api.post('/api/cart/checkout', shippingAddress);
        }
    },

    // ----------------------------------------
    // ORDERS
    // ----------------------------------------
    orders: {
        async list(params = {}) {
            return api.get('/api/orders', params);
        },

        async get(orderId) {
            return api.get(`/api/orders/${orderId}`);
        },

        async create(shippingAddress, comment = null) {
            return api.post('/api/orders', {
                shipping_address: shippingAddress,
                comment
            });
        },

        async cancel(orderId) {
            return api.post(`/api/orders/${orderId}/cancel`);
        },

        async updateStatus(orderId, status, comment = null) {
            return api.put(`/api/orders/${orderId}/status`, {
                status,
                comment
            });
        }
    },

    // ----------------------------------------
    // HEALTH
    // ----------------------------------------
    health: {
        async check() {
            return api.get('/health');
        }
    }
};

// Export
window.API_BASE_URL = API_BASE_URL;
window.TokenManager = TokenManager;
window.APIService = APIService;
window.APIError = APIError;
