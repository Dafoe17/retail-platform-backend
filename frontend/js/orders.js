/**
 * Orders Module - Работа с заказами
 */

const Orders = {
    currentFilters: {
        status: null,
        page: 1,
        page_size: 10
    },
    pagination: {
        total: 0,
        total_pages: 0,
        page: 1,
        page_size: 10
    },

    /**
     * Load orders
     */
    async loadOrders() {
        if (!TokenManager.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        const container = document.querySelector('.orders-list');
        if (!container) return;

        UI.showLoading(container);

        try {
            const response = await APIService.orders.list(this.currentFilters);

            this.pagination = {
                total: response.total,
                total_pages: response.total_pages,
                page: response.page,
                page_size: response.page_size
            };

            UI.hideLoading();
            this.renderOrders(response.items);
            this.renderPagination();

            return response;
        } catch (error) {
            UI.hideLoading();
            console.error('Failed to load orders:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <h3>Ошибка загрузки</h3>
                    <p>Не удалось загрузить заказы. Попробуйте позже.</p>
                    <button class="btn btn-primary" onclick="Orders.loadOrders()">Повторить</button>
                </div>
            `;
        }
    },

    /**
     * Render orders list
     */
    renderOrders(orders) {
        const container = document.querySelector('.orders-list');
        if (!container) return;

        if (!orders || orders.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📋</div>
                    <h3>Заказов пока нет</h3>
                    <p>Оформите первый заказ в нашем магазине</p>
                    <a href="products.html" class="btn btn-primary">Перейти в каталог</a>
                </div>
            `;
            return;
        }

        container.innerHTML = orders.map(order => this.renderOrderCard(order)).join('');
    },

    /**
     * Render single order card
     */
    renderOrderCard(order) {
        const statusClass = Utils.getStatusClass(order.status);
        const statusText = order.status_display || Utils.getStatusText(order.status);
        const itemsWord = Utils.pluralize(order.items.length, 'товар', 'товара', 'товаров');
        const canCancel = ['pending', 'confirmed'].includes(order.status);

        return `
            <div class="order-card" data-order-id="${order.id}">
                <div class="order-header">
                    <div class="order-info">
                        <span class="order-number">Заказ #${order.order_number}</span>
                        <span class="order-date">${Utils.formatDate(order.created_at)}</span>
                    </div>
                    <span class="order-status ${statusClass}">${statusText}</span>
                </div>

                <div class="order-items">
                    ${order.items.slice(0, 3).map(item => `
                        <div class="order-item-mini">
                            <span class="item-name">${Utils.escapeHtml(item.product_name)}</span>
                            <span class="item-qty">×${item.quantity}</span>
                            <span class="item-price">${Utils.formatPrice(item.subtotal)}</span>
                        </div>
                    `).join('')}
                    ${order.items.length > 3 ? `
                        <div class="order-more">и ещё ${order.items.length - 3} ${Utils.pluralize(order.items.length - 3, 'товар', 'товара', 'товаров')}</div>
                    ` : ''}
                </div>

                <div class="order-footer">
                    <div class="order-total">
                        <span>${order.items.length} ${itemsWord} на сумму</span>
                        <strong>${Utils.formatPrice(order.total)}</strong>
                    </div>
                    <div class="order-actions">
                        <button class="btn btn-outline btn-sm" onclick="Orders.showOrderDetails(${order.id})">
                            Подробнее
                        </button>
                        ${canCancel ? `
                            <button class="btn btn-danger btn-sm" onclick="Orders.cancelOrder(${order.id})">
                                Отменить
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Show order details modal
     */
    async showOrderDetails(orderId) {
        const modal = document.createElement('div');
        modal.className = 'order-modal';
        modal.id = 'order-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="Orders.closeModal()"></div>
            <div class="modal-content modal-lg">
                <div class="modal-header">
                    <h2>Детали заказа</h2>
                    <button class="modal-close" onclick="Orders.closeModal()">×</button>
                </div>
                <div class="modal-body">
                    <div class="loading-spinner"></div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        try {
            const order = await APIService.orders.get(orderId);
            const modalBody = modal.querySelector('.modal-body');
            modalBody.innerHTML = this.renderOrderDetails(order);
        } catch (error) {
            modal.querySelector('.modal-body').innerHTML = `
                <div class="error-state">
                    <p>Ошибка загрузки деталей заказа</p>
                    <button class="btn btn-primary" onclick="Orders.closeModal()">Закрыть</button>
                </div>
            `;
        }
    },

    /**
     * Render order details content
     */
    renderOrderDetails(order) {
        const statusClass = Utils.getStatusClass(order.status);
        const statusText = order.status_display || Utils.getStatusText(order.status);

        return `
            <div class="order-details">
                <div class="order-details-header">
                    <div>
                        <h3>Заказ #${order.order_number}</h3>
                        <p class="order-date">от ${Utils.formatDate(order.created_at)}</p>
                    </div>
                    <span class="order-status ${statusClass}">${statusText}</span>
                </div>

                <!-- Status History -->
                ${order.status_history && order.status_history.length > 0 ? `
                    <div class="status-history">
                        <h4>История статусов</h4>
                        <div class="status-timeline">
                            ${order.status_history.map((h, i) => `
                                <div class="status-timeline-item ${i === 0 ? 'current' : ''}">
                                    <div class="status-dot"></div>
                                    <div class="status-content">
                                        <strong>${Utils.getStatusText(h.status)}</strong>
                                        <span class="status-date">${Utils.formatDate(h.changed_at)}</span>
                                        ${h.comment ? `<p class="status-comment">${Utils.escapeHtml(h.comment)}</p>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <!-- Items -->
                <div class="order-items-detail">
                    <h4>Товары</h4>
                    <table class="order-items-table">
                        <thead>
                            <tr>
                                <th>Товар</th>
                                <th>Цена</th>
                                <th>Кол-во</th>
                                <th>Сумма</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${order.items.map(item => `
                                <tr>
                                    <td>${Utils.escapeHtml(item.product_name)}</td>
                                    <td>${Utils.formatPrice(item.unit_price)}</td>
                                    <td>${item.quantity}</td>
                                    <td>${Utils.formatPrice(item.subtotal)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- Totals -->
                <div class="order-totals">
                    <div class="totals-row">
                        <span>Подитог:</span>
                        <span>${Utils.formatPrice(order.subtotal)}</span>
                    </div>
                    ${parseFloat(order.discount) > 0 ? `
                        <div class="totals-row discount">
                            <span>Скидка:</span>
                            <span>-${Utils.formatPrice(order.discount)}</span>
                        </div>
                    ` : ''}
                    ${parseFloat(order.shipping_cost) > 0 ? `
                        <div class="totals-row">
                            <span>Доставка:</span>
                            <span>${Utils.formatPrice(order.shipping_cost)}</span>
                        </div>
                    ` : ''}
                    <div class="totals-row total">
                        <span>Итого:</span>
                        <strong>${Utils.formatPrice(order.total)}</strong>
                    </div>
                </div>

                <!-- Shipping Address -->
                <div class="shipping-address">
                    <h4>Адрес доставки</h4>
                    <p>
                        ${Utils.escapeHtml(order.shipping_address.recipient_name)}<br>
                        ${Utils.escapeHtml(order.shipping_address.street)}, д. ${Utils.escapeHtml(order.shipping_address.building)}
                        ${order.shipping_address.apartment ? `, кв. ${Utils.escapeHtml(order.shipping_address.apartment)}` : ''}<br>
                        ${Utils.escapeHtml(order.shipping_address.city)}, ${Utils.escapeHtml(order.shipping_address.postal_code)}<br>
                        Тел: ${Utils.escapeHtml(order.shipping_address.phone)}
                    </p>
                </div>

                ${order.comment ? `
                    <div class="order-comment">
                        <h4>Комментарий</h4>
                        <p>${Utils.escapeHtml(order.comment)}</p>
                    </div>
                ` : ''}
            </div>
        `;
    },

    /**
     * Close modal
     */
    closeModal() {
        const modal = document.getElementById('order-modal');
        if (modal) {
            modal.remove();
        }
    },

    /**
     * Cancel order
     */
    async cancelOrder(orderId) {
        UI.confirm(
            'Вы уверены, что хотите отменить заказ?',
            async () => {
                try {
                    await APIService.orders.cancel(orderId);
                    UI.success('Заказ отменен');
                    await this.loadOrders();
                } catch (error) {
                    UI.error(error.message || 'Ошибка при отмене заказа');
                }
            }
        );
    },

    /**
     * Filter by status
     */
    filterByStatus(status) {
        this.currentFilters.status = status || null;
        this.currentFilters.page = 1;
        this.loadOrders();
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

        let html = `
            <button class="pagination-btn"
                    onclick="Orders.goToPage(${currentPage - 1})"
                    ${currentPage === 1 ? 'disabled' : ''}>
                ←
            </button>
        `;

        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                html += `
                    <button class="pagination-btn ${i === currentPage ? 'active' : ''}"
                            onclick="Orders.goToPage(${i})">
                        ${i}
                    </button>
                `;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                html += `<span class="pagination-ellipsis">...</span>`;
            }
        }

        html += `
            <button class="pagination-btn"
                    onclick="Orders.goToPage(${currentPage + 1})"
                    ${currentPage === totalPages ? 'disabled' : ''}>
                →
            </button>
        `;

        container.innerHTML = html;
    },

    /**
     * Go to page
     */
    goToPage(page) {
        if (page < 1 || page > this.pagination.total_pages) return;
        this.currentFilters.page = page;
        this.loadOrders();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    /**
     * Initialize orders page
     */
    async init() {
        // Setup status filter
        const statusFilter = document.querySelector('#status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filterByStatus(e.target.value);
            });
        }

        await this.loadOrders();
    }
};

// Export
window.Orders = Orders;
