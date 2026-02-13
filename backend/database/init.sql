-- ============================================
-- ONLINE SHOP DATABASE SCHEMA
-- ============================================

-- ============================================
-- USERS MODULE
-- ============================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'customer',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- User profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    date_of_birth DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Refresh tokens
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(36) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

-- ============================================
-- PRODUCTS MODULE
-- ============================================

-- Categories (иерархия)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    price INTEGER NOT NULL, -- в копейках/центах
    stock INTEGER NOT NULL DEFAULT 0,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    images JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product variants (для разных размеров, цветов и т.д.)
CREATE TABLE IF NOT EXISTS product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) UNIQUE NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    attributes JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- CART MODULE
-- ============================================

-- Carts
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cart items
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    unit_price INTEGER NOT NULL, -- цена на момент добавления (в копейках)
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cart_id, product_id)
);

-- ============================================
-- ORDERS MODULE
-- ============================================

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    subtotal INTEGER NOT NULL, -- в копейках
    shipping_cost INTEGER NOT NULL DEFAULT 0,
    discount INTEGER NOT NULL DEFAULT 0,
    tax INTEGER NOT NULL DEFAULT 0,
    total INTEGER NOT NULL,

    -- Shipping address
    recipient_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    country VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    street VARCHAR(255) NOT NULL,
    building VARCHAR(20) NOT NULL,
    apartment VARCHAR(20),
    postal_code VARCHAR(20) NOT NULL,

    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    product_slug VARCHAR(255),
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL, -- цена на момент заказа (в копейках)
    subtotal INTEGER NOT NULL
);

-- Order status history
CREATE TABLE IF NOT EXISTS order_status_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    comment TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_id ON refresh_tokens(token_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- Products indexes
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_products_is_active ON products(is_active);
CREATE INDEX idx_products_created_at ON products(created_at);

-- Categories indexes
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);

-- Cart indexes
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

-- Orders indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_number ON orders(order_number);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- ============================================
-- TRIGGERS (auto-update updated_at)
-- ============================================

-- Function to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_carts_updated_at BEFORE UPDATE ON carts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SAMPLE DATA (для тестирования)
-- ============================================

-- Insert sample categories
INSERT INTO categories (name, slug, description) VALUES
    ('Электроника', 'electronics', 'Электронные устройства и гаджеты'),
    ('Одежда', 'clothing', 'Одежда для мужчин и женщин'),
    ('Книги', 'books', 'Книги различных жанров')
ON CONFLICT (slug) DO NOTHING;

-- Insert sample products
INSERT INTO products (name, slug, description, price, stock, category_id, images) VALUES
    ('iPhone 15 Pro', 'iphone-15-pro', 'Флагманский смартфон Apple', 9999900, 50, 1, '["https://example.com/iphone.jpg"]'::jsonb),
    ('Samsung Galaxy S24', 'samsung-galaxy-s24', 'Флагманский смартфон Samsung', 8999900, 30, 1, '["https://example.com/samsung.jpg"]'::jsonb),
    ('Футболка базовая', 'basic-tshirt', 'Хлопковая футболка', 199900, 100, 2, '["https://example.com/tshirt.jpg"]'::jsonb),
    ('Джинсы slim', 'slim-jeans', 'Джинсы slim fit', 399900, 75, 2, '["https://example.com/jeans.jpg"]'::jsonb),
    ('Война и мир', 'war-and-peace', 'Роман Льва Толстого', 59900, 200, 3, '["https://example.com/book.jpg"]'::jsonb)
ON CONFLICT (slug) DO NOTHING;

-- Insert sample user (password: password123)
-- bcrypt hash for "password123"
INSERT INTO users (email, password_hash, role, is_active, is_verified) VALUES
    ('user@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Mx5WOWWQWqVG', 'customer', TRUE, TRUE)
ON CONFLICT (email) DO NOTHING;

-- Insert sample orders
INSERT INTO orders (order_number, user_id, status, subtotal, shipping_cost, discount, tax, total, recipient_name, phone, country, city, street, building, postal_code) VALUES
    ('ORD-2024-000001', 1, 'delivered', 599800, 49900, 0, 0, 649700, 'Иван Иванов', '+79001234567', 'Россия', 'Москва', 'Улица Примерная', '123', '123456')
ON CONFLICT (order_number) DO NOTHING;

-- ============================================
-- VIEWS (полезные запросы)
-- ============================================

-- View: Products with category
CREATE OR REPLACE VIEW products_with_category AS
SELECT
    p.*,
    c.name as category_name,
    c.slug as category_slug
FROM products p
LEFT JOIN categories c ON p.category_id = c.id;

-- View: Cart totals
CREATE OR REPLACE VIEW cart_totals AS
SELECT
    c.id as cart_id,
    c.user_id,
    COUNT(ci.id) as items_count,
    COALESCE(SUM(ci.quantity * ci.unit_price), 0) as total_price
FROM carts c
LEFT JOIN cart_items ci ON c.id = ci.cart_id
GROUP BY c.id, c.user_id;

-- View: Order summary
CREATE OR REPLACE VIEW order_summary AS
SELECT
    o.id,
    o.order_number,
    o.user_id,
    u.email as user_email,
    o.status,
    o.total,
    COUNT(oi.id) as items_count,
    o.created_at
FROM orders o
JOIN users u ON o.user_id = u.id
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_number, o.user_id, u.email, o.status, o.total, o.created_at;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Generate order number
CREATE OR REPLACE FUNCTION generate_order_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    year_part VARCHAR(4);
    sequence_part VARCHAR(6);
BEGIN
    year_part := EXTRACT(YEAR FROM CURRENT_TIMESTAMP)::VARCHAR;
    sequence_part := LPAD(NEXTVAL('order_number_seq')::VARCHAR, 6, '0');
    RETURN 'ORD-' || year_part || '-' || sequence_part;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for order numbers
CREATE SEQUENCE IF NOT EXISTS order_number_seq START 1;

-- ============================================
-- END OF INIT SCRIPT
-- ============================================
