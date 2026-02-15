/**
 * Auth Module - Авторизация и управление пользователем
 */

const Auth = {
    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return TokenManager.isAuthenticated();
    },

    /**
     * Get current user from localStorage
     */
    getCurrentUser() {
        const userJson = localStorage.getItem('user');
        return userJson ? JSON.parse(userJson) : null;
    },

    /**
     * Save user to localStorage
     */
    saveUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    /**
     * Clear user data
     */
    clearUser() {
        localStorage.removeItem('user');
    },

    /**
     * Login user
     */
    async login(email, password) {
        try {
            const data = await APIService.auth.login(email, password);

            // Fetch user data after login
            const user = await APIService.auth.getCurrentUser();
            this.saveUser(user);

            return { success: true, data: user };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                error: error.message || 'Ошибка авторизации'
            };
        }
    },

    /**
     * Register new user
     */
    async register(email, password, firstName = null, lastName = null) {
        try {
            const data = await APIService.auth.register(email, password, firstName, lastName);

            // Save user data
            const userData = {
                id: data.id,
                email: data.email,
                role: data.role,
                profile: data.profile
            };
            this.saveUser(userData);

            return { success: true, data: userData };
        } catch (error) {
            console.error('Register error:', error);
            return {
                success: false,
                error: error.message || 'Ошибка регистрации'
            };
        }
    },

    /**
     * Logout user
     */
    async logout() {
        try {
            await APIService.auth.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            this.clearUser();
            window.location.href = 'login.html';
        }
    },

    /**
     * Check auth and redirect if needed
     */
    requireAuth(redirectUrl = 'login.html') {
        if (!this.isAuthenticated()) {
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    },

    /**
     * Redirect authenticated users away from auth pages
     */
    redirectIfAuthenticated(redirectUrl = 'products.html') {
        if (this.isAuthenticated()) {
            window.location.href = redirectUrl;
            return true;
        }
        return false;
    },

    /**
     * Fetch and update current user data
     */
    async fetchCurrentUser() {
        if (!this.isAuthenticated()) {
            return null;
        }

        try {
            const user = await APIService.auth.getCurrentUser();
            this.saveUser(user);
            return user;
        } catch (error) {
            console.error('Failed to fetch user:', error);
            return null;
        }
    },

    /**
     * Check if user has admin role
     */
    isAdmin() {
        const user = this.getCurrentUser();
        return user && user.role === 'admin';
    },

    /**
     * Initialize auth state on page load
     */
    async init() {
        // Try to fetch user data if authenticated
        if (this.isAuthenticated()) {
            const user = await this.fetchCurrentUser();
            if (!user) {
                // Token invalid, clear data
                TokenManager.clearTokens();
                this.clearUser();
            }
        }
    }
};

// ============================================
// LOGIN FORM HANDLER
// ============================================

async function handleLoginForm(event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const email = form.querySelector('#email').value.trim();
    const password = form.querySelector('#password').value;

    // Clear previous errors
    FormHelpers.clearFormErrors(form);

    // Validate
    let hasErrors = false;

    if (!email) {
        FormHelpers.showFieldError('#email', 'Введите email');
        hasErrors = true;
    } else if (!FormHelpers.isValidEmail(email)) {
        FormHelpers.showFieldError('#email', 'Некорректный email');
        hasErrors = true;
    }

    if (!password) {
        FormHelpers.showFieldError('#password', 'Введите пароль');
        hasErrors = true;
    }

    if (hasErrors) return;

    // Show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Вход...';

    try {
        const result = await Auth.login(email, password);

        if (result.success) {
            UI.success('Добро пожаловать!');
            setTimeout(() => {
                window.location.href = 'products.html';
            }, 500);
        } else {
            UI.error(result.error);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Войти';
        }
    } catch (error) {
        UI.error('Произошла ошибка при входе');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Войти';
    }
}

// ============================================
// REGISTER FORM HANDLER
// ============================================

async function handleRegisterForm(event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const email = form.querySelector('#email').value.trim();
    const password = form.querySelector('#password').value;
    const confirmPassword = form.querySelector('#confirm_password')?.value;
    const firstName = form.querySelector('#first_name')?.value.trim();
    const lastName = form.querySelector('#last_name')?.value.trim();

    // Clear previous errors
    FormHelpers.clearFormErrors(form);

    // Validate
    let hasErrors = false;

    if (!email) {
        FormHelpers.showFieldError('#email', 'Введите email');
        hasErrors = true;
    } else if (!FormHelpers.isValidEmail(email)) {
        FormHelpers.showFieldError('#email', 'Некорректный email');
        hasErrors = true;
    }

    if (!password) {
        FormHelpers.showFieldError('#password', 'Введите пароль');
        hasErrors = true;
    } else if (!FormHelpers.isValidPassword(password)) {
        FormHelpers.showFieldError('#password', 'Пароль должен быть минимум 8 символов');
        hasErrors = true;
    }

    if (confirmPassword !== undefined && password !== confirmPassword) {
        FormHelpers.showFieldError('#confirm_password', 'Пароли не совпадают');
        hasErrors = true;
    }

    if (hasErrors) return;

    // Show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Регистрация...';

    try {
        const result = await Auth.register(email, password, firstName, lastName);

        if (result.success) {
            UI.success('Регистрация успешна!');
            setTimeout(() => {
                window.location.href = 'products.html';
            }, 500);
        } else {
            UI.error(result.error);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Зарегистрироваться';
        }
    } catch (error) {
        UI.error('Произошла ошибка при регистрации');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Зарегистрироваться';
    }
}

// Export
window.Auth = Auth;
window.handleLoginForm = handleLoginForm;
window.handleRegisterForm = handleRegisterForm;
