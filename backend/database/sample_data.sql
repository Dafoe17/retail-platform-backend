-- Тестовые данные для Retail Platform
-- Выполните: psql -U username -d database_name -f sample_data.sql

-- Включить расширения
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =================== КАТЕГОРИИ ===================

INSERT INTO categories (name, slug, description, is_active, created_at) VALUES
('Электроника', 'elektronika', 'Смартфоны, ноутбуки и другие электронные устройства', true, NOW()),
('Одежда', 'odezhda', 'Одежда для мужчин и женщин', true, NOW()),
('Бытовая техника', 'byitovaya-tehnika', 'Техника для дома', true, NOW()),
('Книги', 'knigi', 'Книги различных жанров', true, NOW()),
('Спорт и отдых', 'sport-i-otdyh', 'Товары для спорта и отдыха', true, NOW()),
('Красота и здоровье', 'krasota-i-zdorove', 'Косметика и товары для здоровья', true, NOW())
ON CONFLICT (slug) DO NOTHING;

-- =================== ПРОДУКТЫ ===================

-- Электроника
INSERT INTO products (name, slug, description, price, stock, category_id, images, is_active, created_at, updated_at) VALUES
('iPhone 15 Pro 256GB', 'iphone-15-pro-256gb',
'Смартфон Apple iPhone 15 Pro с дисплеем 6.1 дюйма, камерой 48 Мп и процессором A17 Pro.',
9999000, 50, 1, '["https://images.unsplash.com/photo-1592750475338-74b7b210f4f7?w=400"]', true, NOW(), NOW()),

('Samsung Galaxy S24 Ultra', 'samsung-galaxy-s24-ultra',
'Флагман Samsung с экраном 6.8 дюйма, камерой 200 Мп и S Pen.',
8999000, 35, 1, '["https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400"]', true, NOW(), NOW()),

('MacBook Air 13" M3', 'macbook-air-13-m3',
'Облегченный ноутбук Apple с процессором M3, 8 ГБ RAM и 256 ГБ SSD.',
12999000, 20, 1, '["https://images.unsplash.com/photo-1517336714731-489679fd1ca8?w=400"]', true, NOW(), NOW()),

-- Одежда
('Классический худи черного цвета', 'hudi-chernyy',
'Удобный худи из хлопка 100%. Идеален для повседневной носки.',
399900, 100, 2, '["https://images.unsplash.com/photo-1556821840-022fac958a99?w=400"]', true, NOW(), NOW()),

('Джинсы slim fit', 'dzhinsy-slim-fit',
'Классические джинсы прямого кроя из денима. Размеры: 28-34.',
299900, 80, 2, '["https://images.unsplash.com/photo-1542272604-787c3835535d?w=400"]', true, NOW(), NOW()),

('Кофта с капюшоном', 'kofta-s-kapyushonom',
'Теплая кофта с капюшоном для прохладной погоды. Состав: хлопок 80%, шерсть 20%.',
599900, 60, 2, '["https://images.unsplash.com/photo-1556905055-2f1480df5c44?w=400"]', true, NOW(), NOW()),

-- Бытовая техника
('Робот-пылесос Xiaomi', 'robot-pylesos-xiaomi',
'Автоматический робот-пылесос с навигацией LDS, мощностью 2100 Па.',
2499000, 25, 3, '["https://images.unsplash.com/photo-1558618666-f76279422b5a?w=400"]', true, NOW(), NOW()),

('Умная колонка Яндекс Станция Макс', 'yandex-stanciya-maks',
'Умная колонка с голосовым помощником Алиса, 60 Вт мощности.',
3499000, 40, 3, '["https://images.unsplash.com/photo-1589492477829-5ee9a5c6e45d?w=400"]', true, NOW(), NOW()),

('Фен Dyson Supersonic', 'fen-dyson-supersonic',
'Профессиональный фен с умным контролем температуры и ионизацией.',
2999000, 15, 3, '["https://images.unsplash.com/photo-1522338188442-1e2e3a72f8f9?w=400"]', true, NOW(), NOW()),

-- Книги
('Мастер и Маргарита. М.А. Булгаков', 'master-i-margarita',
'Роман Михаила Булгакова. Перепечатка. Твердый переплет.',
89900, 200, 4, '["https://images.unsplash.com/photo-1512820790803-83ca734de79d?w=400"]', true, NOW(), NOW()),

('Властелин колец. Дж.Р.Р. Толкин', 'vlactelin-kolec',
'Роман-эпопея Дж.Р.Р. Толкина. Полное собрание в трех томах.',
129900, 150, 4, '["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400"]', true, NOW(), NOW()),

('Код Да Винчи. Дэн Браун', 'kod-da-vinchi',
'Детективный роман Дэна Брауна. Бестселлер по всему миру.',
69900, 180, 4, '["https://images.unsplash.com/photo-1589829085413-56de8ae18c29?w=400"]', true, NOW(), NOW()),

-- Спорт
('Йога-мат премиум', 'yoga-mat-premium',
'Мат для йоги из экологического материала ТПЭ. Размер: 183x61 см, толщина 6 мм.',
199900, 90, 5, '["https://images.unsplash.com/photo-1601925261366-7df1bc1dbe51?w=400"]', true, NOW(), NOW()),

('Гантели 2 кг хром', 'ganteli-2kg-hrom',
'Комплект гантелей по 2 кг для фитнес-тренировок в домашних условиях.',
79900, 120, 5, '["https://images.unsplash.com/photo-1517927217850-9c592e83af84?w=400"]', true, NOW(), NOW()),

('Велосипед дорожный', 'velosiped-dorozhnyy',
'Дорожный велосипед с алюминиевой рамой, 21 скорость, размер 28 дюймов.',
2999000, 12, 5, '["https://images.unsplash.com/photo-1532235289296-ecf7a1ca42ca?w=400"]', true, NOW(), NOW()),

-- Красота
('Парфюмерный набор Chanel', 'parfyumernyy-nabor-chanel',
'Набор из трех ароматов: Chanel No.5, Coco Mademoiselle, Bleu de Chanel.',
4999000, 30, 6, '["https://images.unsplash.com/photo-1541643600914-78a8685c2f0d?w=400"]', true, NOW(), NOW()),

('Набор косметики MAC', 'nabor-kosmetiki-mac',
'Профессиональный набор косметики MAC: тональник, помады, тушь.',
3499000, 45, 6, '["https://images.unsplash.com/photo-1512496015851-a90fb94ba6f7?w=400"]', true, NOW(), NOW()),

('Шампунь и кондиционер Loreal', 'shampun-i-kondicioner-loreal',
'Набор для волос: шампунь 400мл + кондиционер 400мл. Для всех типов волос.',
99900, 200, 6, '["https://images.unsplash.com/photo-1596462502292-c2f2caa6cc38?w=400"]', true, NOW(), NOW())

ON CONFLICT (slug) DO NOTHING;

INSERT INTO users (email, password_hash, role, is_active, is_verified, created_at) VALUES
('test@example.com', '$2b$12$LQv3c1yqBWVHxmd0VHW1O9qWBz.HfWKR.k', 'customer', true, true, NOW()),
('admin@example.com', '$2b$12$LQv3c1yqBWVHxmd0VHW1O9qWBz.HfWKR.k', 'admin', true, true, NOW())
ON CONFLICT (email) DO NOTHING;

INSERT INTO user_profiles (user_id, first_name, last_name, phone) VALUES
(1, 'Иван', 'Иванов', '+79991234567'),
(2, 'Администратор', 'Системы', '+799976543210')
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO orders (order_number, user_id, status, subtotal, shipping_cost, discount, tax, total,
    recipient_name, phone, country, city, street, building, apartment, postal_code, created_at, updated_at)
VALUES
('ORD-001-TEST', 1, 'delivered', 999900, 0, 0, 0, 999900,
 'Иван Иванов', '+79991234567', 'Россия', 'Москва', 'Тверская', '1', '10', '125009',
 NOW(), NOW())
ON CONFLICT (order_number) DO NOTHING;
