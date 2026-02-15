/**
 * Theme Module - Управление темной/светлой темой
 */

const Theme = {
    STORAGE_KEY: 'theme',
    DARK_THEME: 'dark',
    LIGHT_THEME: 'light',

    /**
     * Get current theme from storage
     */
    getStoredTheme() {
        return localStorage.getItem(this.STORAGE_KEY);
    },

    /**
     * Get system preferred theme
     */
    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? this.DARK_THEME
            : this.LIGHT_THEME;
    },

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || this.LIGHT_THEME;
    },

    /**
     * Set theme
     */
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.STORAGE_KEY, theme);
        this.updateToggleButton();
    },

    /**
     * Toggle theme
     */
    toggle() {
        const currentTheme = this.getCurrentTheme();
        const newTheme = currentTheme === this.DARK_THEME ? this.LIGHT_THEME : this.DARK_THEME;
        this.setTheme(newTheme);
    },

    /**
     * Update toggle button icon
     */
    updateToggleButton() {
        const button = document.querySelector('.theme-toggle');
        if (!button) return;

        const currentTheme = this.getCurrentTheme();
        const icon = currentTheme === this.DARK_THEME ? '☀️' : '🌙';
        const title = currentTheme === this.DARK_THEME ? 'Светлая тема' : 'Тёмная тема';

        button.innerHTML = icon;
        button.setAttribute('title', title);
        button.setAttribute('aria-label', title);
    },

    /**
     * Create toggle button if not exists
     */
    createToggleButton() {
        if (document.querySelector('.theme-toggle')) return;

        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('type', 'button');
        button.onclick = () => this.toggle();

        document.body.appendChild(button);
        this.updateToggleButton();
    },

    /**
     * Initialize theme
     */
    init() {
        // Get stored theme or system preference
        const storedTheme = this.getStoredTheme();
        const initialTheme = storedTheme || this.LIGHT_THEME;

        // Apply theme
        this.setTheme(initialTheme);

        // Create toggle button
        this.createToggleButton();

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.getStoredTheme()) {
                this.setTheme(e.matches ? this.DARK_THEME : this.LIGHT_THEME);
            }
        });
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    Theme.init();
});

// Export
window.Theme = Theme;
