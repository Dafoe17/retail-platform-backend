/**
 * Products Module - Работа с товарами
 */

const Products = {
    // State
    categories: [],
    currentFilters: {
        category_id: null,
        min_price: null,
        max_price: null,
        in_stock: null,
        search: '',
        sort_by: 'created',
        page: 1,
        page_size: 12
    },
    pagination: {
        total: 0,
        total_pages: 0,
        page: 1,
        page_size: 12
    },

    /**
     * Load categories
     */
    async loadCategories() {
        try {
            this.categories = await APIService.products.getCategories();
            return this.categories;
        } catch (error) {
            console.error('Failed to load categories:', error);
            return [];
        }
    },

    /**
     * Load products with current filters
     */
    async loadProducts() {
        const container = document.querySelector('.products-grid');
        if (!container) return;

        UI.showLoading(container);

        try {
            const response = await APIService.products.list(this.currentFilters);

            this.pagination = {
                total: response.total,
                total_pages: response.total_pages,
                page: response.page,
                page_size: response.page_size
            };

            UI.hideLoading();
            this.renderProducts(response.items);
            this.renderPagination();

            return response;
        } catch (error) {
            UI.hideLoading();
            console.error('Failed to load products:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <h3>Ошибка загрузки</h3>
                    <p>Не удалось загрузить товары. Попробуйте позже.</p>
                    <button class="btn btn-primary" onclick="Products.loadProducts()">Повторить</button>
                </div>
            `;
        }
    },

    /**
     * Render products grid
     */
    renderProducts(products) {
        const container = document.querySelector('.products-grid');
        if (!container) return;

        if (!products || products.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <h3>Товары не найдены</h3>
                    <p>Попробуйте изменить параметры поиска</p>
                </div>
            `;
            return;
        }

        container.innerHTML = products.map(product => this.renderProductCard(product)).join('');
    },

    /**
     * Render single product card
     */
    renderProductCard(product) {
        const imageUrl = product.images && product.images.length > 0
            ? product.images[0]
            : 'https://via.placeholder.com/300x300?text=No+Image';

        const categoryName = product.category?.name || '';
        const isOutOfStock = product.stock === 0;

        return `
            <div class="product-card ${isOutOfStock ? 'out-of-stock' : ''}" data-product-id="${product.id}">
                <div class="product-image">
                    <img src="${Utils.escapeHtml(imageUrl)}" alt="${Utils.escapeHtml(product.name)}" loading="lazy">
                    ${isOutOfStock ? '<span class="product-badge badge-out">Нет в наличии</span>' : ''}
                    ${product.stock > 0 && product.stock <= 5 ? '<span class="product-badge badge-low">Осталось ' + product.stock + ' шт.</span>' : ''}
                </div>
                <div class="product-info">
                    ${categoryName ? `<span class="product-category">${Utils.escapeHtml(categoryName)}</span>` : ''}
                    <h3 class="product-name">
                        <a href="product-detail.html?id=${product.id}">${Utils.escapeHtml(product.name)}</a>
                    </h3>
                    ${product.description ? `<p class="product-description">${Utils.escapeHtml(Utils.truncate(product.description, 80))}</p>` : ''}
                    <div class="product-footer">
                        <span class="product-price">${Utils.formatPrice(product.price)}</span>
                        <button class="btn btn-primary btn-sm add-to-cart-btn"
                                onclick="Products.addToCart(${product.id}, event)"
                                ${isOutOfStock ? 'disabled' : ''}>
                            ${isOutOfStock ? 'Нет в наличии' : 'В корзину'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Render categories filter
     */
    renderCategoriesFilter() {
        const container = document.querySelector('.categories-filter');
        if (!container) return;

        let html = `
            <button class="filter-btn ${!this.currentFilters.category_id ? 'active' : ''}"
                    onclick="Products.filterByCategory(null)">
                Все товары
            </button>
        `;

        html += this.categories.map(category => `
            <button class="filter-btn ${this.currentFilters.category_id === category.id ? 'active' : ''}"
                    onclick="Products.filterByCategory(${category.id})">
                ${Utils.escapeHtml(category.name)}
            </button>
        `).join('');

        container.innerHTML = html;
    },

    /**
     * Render pagination
     */
    renderPagination() {
        const container = document.querySelector('.pagination');
        if (!container) return;

        if (this.pagination.total_pages <= 1) {
            container.innerHTML = '';
            return;
        }

        const currentPage = this.pagination.page;
        const totalPages = this.pagination.total_pages;

        let html = '';

        // Previous button
        html += `
            <button class="pagination-btn"
                    onclick="Products.goToPage(${currentPage - 1})"
                    ${currentPage === 1 ? 'disabled' : ''}>
                ←
            </button>
        `;

        // Page numbers
        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage < maxVisiblePages - 1) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        if (startPage > 1) {
            html += `<button class="pagination-btn" onclick="Products.goToPage(1)">1</button>`;
            if (startPage > 2) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <button class="pagination-btn ${i === currentPage ? 'active' : ''}"
                        onclick="Products.goToPage(${i})">
                    ${i}
                </button>
            `;
        }

        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
            html += `<button class="pagination-btn" onclick="Products.goToPage(${totalPages})">${totalPages}</button>`;
        }

        // Next button
        html += `
            <button class="pagination-btn"
                    onclick="Products.goToPage(${currentPage + 1})"
                    ${currentPage === totalPages ? 'disabled' : ''}>
                →
            </button>
        `;

        container.innerHTML = html;

        // Update results info
        const resultsInfo = document.querySelector('.results-info');
        if (resultsInfo) {
            const from = (currentPage - 1) * this.pagination.page_size + 1;
            const to = Math.min(currentPage * this.pagination.page_size, this.pagination.total);
            resultsInfo.textContent = `Показано ${from}-${to} из ${this.pagination.total} товаров`;
        }
    },

    /**
     * Go to page
     */
    goToPage(page) {
        if (page < 1 || page > this.pagination.total_pages) return;
        this.currentFilters.page = page;
        URLHelpers.setQueryParam('page', page > 1 ? page : null);
        this.loadProducts();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    /**
     * Filter by category
     */
    filterByCategory(categoryId) {
        this.currentFilters.category_id = categoryId;
        this.currentFilters.page = 1;
        URLHelpers.setQueryParam('category', categoryId);
        URLHelpers.setQueryParam('page', null);
        this.renderCategoriesFilter();
        this.loadProducts();
    },

    /**
     * Search products
     */
    searchProducts: Utils.debounce(function(query) {
        Products.currentFilters.search = query;
        Products.currentFilters.page = 1;
        URLHelpers.setQueryParam('search', query || null);
        URLHelpers.setQueryParam('page', null);
        Products.loadProducts();
    }, 300),

    /**
     * Sort products
     */
    sortProducts(sortBy) {
        this.currentFilters.sort_by = sortBy;
        this.currentFilters.page = 1;
        URLHelpers.setQueryParam('sort', sortBy !== 'created' ? sortBy : null);
        URLHelpers.setQueryParam('page', null);
        this.loadProducts();
    },

    /**
     * Filter by stock
     */
    filterInStock(onlyInStock) {
        this.currentFilters.in_stock = onlyInStock ? true : null;
        this.currentFilters.page = 1;
        URLHelpers.setQueryParam('in_stock', onlyInStock ? 'true' : null);
        URLHelpers.setQueryParam('page', null);
        this.loadProducts();
    },

    /**
     * Add product to cart
     */
    async addToCart(productId, event) {
        if (event) {
            event.preventDefault();
            event.stopPropagation();
        }

        if (!TokenManager.isAuthenticated()) {
            UI.confirm(
                'Для добавления товаров в корзину необходимо войти в аккаунт',
                () => { window.location.href = 'login.html'; }
            );
            return;
        }

        const btn = event?.target;
        if (btn) {
            btn.disabled = true;
            btn.textContent = 'Добавление...';
        }

        try {
            await APIService.cart.addItem(productId, 1);
            UI.success('Товар добавлен в корзину');
            UI.updateCartBadge();

            if (btn) {
                btn.textContent = 'Добавлено ✓';
                setTimeout(() => {
                    btn.disabled = false;
                    btn.textContent = 'В корзину';
                }, 1500);
            }
        } catch (error) {
            UI.error(error.message || 'Ошибка при добавлении в корзину');
            if (btn) {
                btn.disabled = false;
                btn.textContent = 'В корзину';
            }
        }
    },

    /**
     * Initialize products page
     */
    async init() {
        // Load categories first
        await this.loadCategories();
        this.renderCategoriesFilter();

        // Apply URL filters
        const urlParams = URLHelpers.getQueryParams();
        if (urlParams.category) {
            this.currentFilters.category_id = parseInt(urlParams.category);
        }
        if (urlParams.search) {
            this.currentFilters.search = urlParams.search;
            const searchInput = document.querySelector('#search-input');
            if (searchInput) {
                searchInput.value = urlParams.search;
            }
        }
        if (urlParams.sort) {
            this.currentFilters.sort_by = urlParams.sort;
            const sortSelect = document.querySelector('#sort-select');
            if (sortSelect) {
                sortSelect.value = urlParams.sort;
            }
        }
        if (urlParams.page) {
            this.currentFilters.page = parseInt(urlParams.page);
        }
        if (urlParams.in_stock === 'true') {
            this.currentFilters.in_stock = true;
            const inStockCheckbox = document.querySelector('#in-stock-filter');
            if (inStockCheckbox) {
                inStockCheckbox.checked = true;
            }
        }

        // Load products
        await this.loadProducts();

        // Setup search input
        const searchInput = document.querySelector('#search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchProducts(e.target.value);
            });
        }

        // Setup sort select
        const sortSelect = document.querySelector('#sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortProducts(e.target.value);
            });
        }

        // Setup in-stock filter
        const inStockFilter = document.querySelector('#in-stock-filter');
        if (inStockFilter) {
            inStockFilter.addEventListener('change', (e) => {
                this.filterInStock(e.target.checked);
            });
        }
    }
};

// Export
window.Products = Products;
