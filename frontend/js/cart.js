/**
 * Cart Module - Работа с корзиной
 */

const Cart = {
    cartData: null,

    /**
     * Load cart data
     */
    async loadCart() {
        if (!TokenManager.isAuthenticated()) {
            window.location.href = 'login.html';
            return;
        }

        const container = document.querySelector('.cart-content');
        if (!container) return;

        UI.showLoading(container);

        try {
            this.cartData = await APIService.cart.get();
            UI.hideLoading();
            this.renderCart();
            return this.cartData;
        } catch (error) {
            UI.hideLoading();
            console.error('Failed to load cart:', error);
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">🛒</div>
                    <h3>Ошибка загрузки</h3>
                    <p>Не удалось загрузить корзину. Попробуйте позже.</p>
                    <button class="btn btn-primary" onclick="Cart.loadCart()">Повторить</button>
                </div>
            `;
        }
    },

    /**
     * Render cart
     */
    renderCart() {
        const container = document.querySelector('.cart-content');
        if (!container) return;

        if (!this.cartData || !this.cartData.items || this.cartData.items.length === 0) {
            container.innerHTML = `
                <div class="cart-empty">
                    <div class="empty-state">
                        <div class="empty-state-icon">🛒</div>
                        <h3>Корзина пуста</h3>
                        <p>Добавьте товары из каталога</p>
                        <a href="products.html" class="btn btn-primary">Перейти в каталог</a>
                    </div>
                </div>
            `;

            // Hide summary
            const summary = document.querySelector('.cart-summary');
            if (summary) summary.style.display = 'none';

            return;
        }

        // Show summary
        const summary = document.querySelector('.cart-summary');
        if (summary) summary.style.display = 'block';

        container.innerHTML = `
            <div class="cart-items">
                ${this.cartData.items.map(item => this.renderCartItem(item)).join('')}
            </div>
        `;

        this.renderSummary();
    },

    /**
     * Render single cart item
     */
    renderCartItem(item) {
        const imageUrl = item.product_image || 'https://via.placeholder.com/100x100?text=No+Image';

        return `
            <div class="cart-item ${!item.is_available ? 'item-unavailable' : ''}" data-item-id="${item.id}">
                <div class="cart-item-image">
                    <img src="${Utils.escapeHtml(imageUrl)}" alt="${Utils.escapeHtml(item.product_name)}">
                </div>
                <div class="cart-item-info">
                    <h4 class="cart-item-name">${Utils.escapeHtml(item.product_name)}</h4>
                    <p class="cart-item-price">${Utils.formatPrice(item.unit_price)} за шт.</p>
                    ${!item.is_available ? '<span class="item-unavailable-badge">Товар недоступен</span>' : ''}
                    ${item.stock_available < item.quantity ? `<span class="item-warning">Доступно: ${item.stock_available} шт.</span>` : ''}
                </div>
                <div class="cart-item-quantity">
                    <div class="quantity-control">
                        <button class="quantity-btn" onclick="Cart.updateQuantity(${item.id}, ${item.quantity - 1})"
                                ${item.quantity <= 1 ? 'disabled' : ''}>−</button>
                        <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="${item.stock_available}"
                               onchange="Cart.updateQuantity(${item.id}, parseInt(this.value))">
                        <button class="quantity-btn" onclick="Cart.updateQuantity(${item.id}, ${item.quantity + 1})"
                                ${item.quantity >= item.stock_available ? 'disabled' : ''}>+</button>
                    </div>
                </div>
                <div class="cart-item-subtotal">
                    <span class="subtotal-value">${Utils.formatPrice(item.subtotal)}</span>
                </div>
                <button class="cart-item-remove" onclick="Cart.removeItem(${item.id})" title="Удалить">
                    ×
                </button>
            </div>
        `;
    },

    /**
     * Render cart summary
     */
    renderSummary() {
        const container = document.querySelector('.cart-summary');
        if (!container || !this.cartData) return;

        const itemsCount = this.cartData.items_count || 0;
        const itemsWord = Utils.pluralize(itemsCount, 'товар', 'товара', 'товаров');

        container.innerHTML = `
            <h3 class="summary-title">Итого</h3>
            <div class="summary-row">
                <span>${itemsCount} ${itemsWord}</span>
                <span>${Utils.formatPrice(this.cartData.total)}</span>
            </div>
            <div class="summary-total">
                <span>К оплате:</span>
                <span class="total-value">${Utils.formatPrice(this.cartData.total)}</span>
            </div>
            <button class="btn btn-primary btn-block checkout-btn" onclick="Cart.showCheckoutForm()">
                Оформить заказ
            </button>
            <button class="btn btn-outline btn-block" onclick="Cart.clearCart()">
                Очистить корзину
            </button>
        `;
    },

    /**
     * Update item quantity
     */
    async updateQuantity(itemId, newQuantity) {
        if (newQuantity < 1) {
            this.removeItem(itemId);
            return;
        }

        try {
            this.cartData = await APIService.cart.updateItem(itemId, newQuantity);
            this.renderCart();
            UI.updateCartBadge();
        } catch (error) {
            UI.error(error.message || 'Ошибка при обновлении количества');
        }
    },

    /**
     * Remove item from cart
     */
    async removeItem(itemId) {
        UI.confirm(
            'Удалить товар из корзины?',
            async () => {
                try {
                    this.cartData = await APIService.cart.removeItem(itemId);
                    this.renderCart();
                    UI.updateCartBadge();
                    UI.success('Товар удален из корзины');
                } catch (error) {
                    UI.error(error.message || 'Ошибка при удалении товара');
                }
            }
        );
    },

    /**
     * Clear entire cart
     */
    async clearCart() {
        UI.confirm(
            'Очистить всю корзину?',
            async () => {
                try {
                    await APIService.cart.clear();
                    this.cartData = { items: [], total: 0, items_count: 0 };
                    this.renderCart();
                    UI.updateCartBadge();
                    UI.success('Корзина очищена');
                } catch (error) {
                    UI.error(error.message || 'Ошибка при очистке корзины');
                }
            }
        );
    },

    /**
     * Show checkout form
     */
    showCheckoutForm() {
        if (!this.cartData || this.cartData.items.length === 0) {
            UI.warning('Корзина пуста');
            return;
        }

        // Check for unavailable items
        const unavailableItems = this.cartData.items.filter(item => !item.is_available);
        if (unavailableItems.length > 0) {
            UI.error('В корзине есть недоступные товары. Удалите их перед оформлением.');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'checkout-modal';
        modal.id = 'checkout-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="Cart.closeCheckoutForm()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Оформление заказа</h2>
                    <button class="modal-close" onclick="Cart.closeCheckoutForm()">×</button>
                </div>
                <form id="checkout-form" onsubmit="Cart.handleCheckout(event)">
                    <div class="modal-body">
                        <h4>Адрес доставки</h4>

                        <div class="form-group">
                            <label for="recipient_name">Получатель *</label>
                            <input type="text" id="recipient_name" name="recipient_name" required
                                   placeholder="ФИО получателя">
                        </div>

                        <div class="form-group">
                            <label for="phone">Телефон *</label>
                            <input type="tel" id="phone" name="phone" required
                                   placeholder="+7 (999) 123-45-67" minlength="10">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="postal_code">Индекс *</label>
                                <input type="text" id="postal_code" name="postal_code" required
                                       placeholder="123456">
                            </div>
                            <div class="form-group">
                                <label for="city">Город *</label>
                                <input type="text" id="city" name="city" required
                                       placeholder="Москва">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="street">Улица *</label>
                            <input type="text" id="street" name="street" required
                                   placeholder="Название улицы">
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label for="building">Дом *</label>
                                <input type="text" id="building" name="building" required
                                       placeholder="1">
                            </div>
                            <div class="form-group">
                                <label for="apartment">Квартира</label>
                                <input type="text" id="apartment" name="apartment"
                                       placeholder="1">
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="comment">Комментарий к заказу</label>
                            <textarea id="comment" name="comment" rows="3"
                                      placeholder="Дополнительная информация"></textarea>
                        </div>

                        <div class="checkout-summary">
                            <p>Товаров: ${this.cartData.items_count}</p>
                            <p class="checkout-total">Итого: ${Utils.formatPrice(this.cartData.total)}</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline" onclick="Cart.closeCheckoutForm()">
                            Отмена
                        </button>
                        <button type="submit" class="btn btn-primary">
                            Подтвердить заказ
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);
    },

    /**
     * Close checkout form
     */
    closeCheckoutForm() {
        const modal = document.getElementById('checkout-modal');
        if (modal) {
            modal.remove();
        }
    },

    /**
     * Handle checkout form submission
     */
    async handleCheckout(event) {
        event.preventDefault();

        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const formData = FormHelpers.getFormData(form);

        // Validate required fields
        if (!formData.recipient_name || !formData.phone || !formData.city ||
            !formData.street || !formData.building || !formData.postal_code) {
            UI.error('Заполните все обязательные поля');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Оформление...';

        const shippingAddress = {
            recipient_name: formData.recipient_name,
            phone: formData.phone,
            postal_code: formData.postal_code,
            city: formData.city,
            street: formData.street,
            building: formData.building,
            apartment: formData.apartment || null,
            country: 'Россия'
        };

        try {
            const order = await APIService.cart.checkout(shippingAddress);

            this.closeCheckoutForm();
            UI.success(`Заказ #${order.order_number} успешно оформлен!`);
            UI.updateCartBadge();

            // Redirect to order page
            setTimeout(() => {
                window.location.href = `orders.html`;
            }, 1500);
        } catch (error) {
            UI.error(error.message || 'Ошибка при оформлении заказа');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Подтвердить заказ';
        }
    },

    /**
     * Initialize cart page
     */
    async init() {
        await this.loadCart();
    }
};

// Export
window.Cart = Cart;
