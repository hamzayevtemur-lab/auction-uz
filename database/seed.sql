USE auction_uz;

-- Kategoriyalar
INSERT INTO categories (name_uz, name_ru, icon, slug) VALUES
('Elektronika',    'Электроника',  '📱', 'electronics'),
('Avtomobil',      'Автомобиль',   '🚗', 'auto'),
('Ko''chmas mulk', 'Недвижимость', '🏠', 'realestate'),
('Kiyim-kechak',   'Одежда',       '👗', 'clothing'),
('San''at',        'Искусство',    '🎨', 'art'),
('Zargarlik',      'Ювелирные',    '💍', 'jewelry'),
('Mebel',          'Мебель',       '🪑', 'furniture'),
('Sport',          'Спорт',        '⚽', 'sport'),
('Kitob',          'Книги',        '📚', 'books'),
('Boshqa',         'Другое',       '🔧', 'other')
ON DUPLICATE KEY UPDATE name_uz = VALUES(name_uz);

-- Foydalanuvchilar
-- Barcha parollar: test1234 (bcrypt 5.0.0 bilan hash qilingan)
INSERT INTO users (full_name, email, phone, password, role, is_verified, balance) VALUES
('Admin User',
 'admin@savdo.uz', '+998901234567',
 '$2b$12$EC7P6Toc03U7zbd5TjZyGuL4nPpbi8Tjvolho0yFKMM/FhYln9jBW',
 'admin', TRUE, 0),

('Jasur Karimov',
 'jasur@test.uz', '+998901111111',
 '$2b$12$wGNdguE7rbchHTtaBrRQe.tyDgS5LjyoUgOLCKam2g4oWjShmPDyy',
 'buyer', TRUE, 5000000),

('Malika Rahimova',
 'malika@test.uz', '+998902222222',
 '$2b$12$SqxpBB1cmU8kEjTCBnjvo.KHtSnuBGn5OftLsrVNJBMEY7ae1XvT.',
 'seller', TRUE, 0),

('Bobur Sobirov',
 'bobur@test.uz', '+998903333333',
 '$2b$12$0ADhRVMxt0nTAm8w/daMTu46Wbu6LL.zIBpRK5q144MAdrs9U/xIK',
 'seller', TRUE, 0),

('Nilufar Azimova',
 'nilufar@test.uz', '+998904444444',
 '$2b$12$t6PD3ELdBj4xgTuEwlx3f.dhkkG1FRs2/Nn4H/JIOjX.i0I1GHZym',
 'buyer', TRUE, 3000000)

ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- Auktsionlar
INSERT INTO auctions
  (seller_id, category_id, title, description, item_condition, location, delivery,
   starting_price, min_step, current_bid, status,
   starts_at, ends_at, seller_fee_paid, seller_fee_amount)
VALUES
(3, 1,
 'iPhone 15 Pro Max 256GB Natural Titanium',
 'Apple iPhone 15 Pro Max 256GB. Toliq kafolat bilan. Quticha ochilmagan. A17 Pro chip, 48MP kamera.',
 'Yangi (quti ochilmagan)', 'Toshkent, Yunusobod', 'Bor (xaridor tolaydi)',
 8500000, 100000, 9200000, 'active',
 NOW() - INTERVAL 1 DAY, NOW() + INTERVAL 3 DAY, TRUE, 85000),

(3, 5,
 'Vintage Uzbek Gilami XIX asr',
 'XIX asr Fargona viloyatida toqilgan. Naturel boyoqlar. 280x180 sm. Autentifikatsiya qilingan.',
 'Antik / Vintage', 'Toshkent, Mirzo Ulugbek', 'Kelishiladi',
 3200000, 50000, 4100000, 'active',
 NOW() - INTERVAL 2 DAY, NOW() + INTERVAL 1 DAY, TRUE, 32000),

(4, 1,
 'Samsung 65 dyuym QLED 4K Smart TV 2024',
 'Samsung QN65Q80C. 4K QLED, 120Hz, HDR10+, Tizen OS. 2024-yil modeli.',
 'Yangi kabi', 'Samarqand', 'Bor (sotuvchi tolaydi)',
 12000000, 200000, 12800000, 'active',
 NOW() - INTERVAL 3 DAY, NOW() + INTERVAL 5 DAY, TRUE, 120000),

(4, 1,
 'MacBook Pro M3 14 dyuym 512GB Space Black',
 'Apple MacBook Pro M3 chip, 16GB RAM, 512GB SSD. 2024-yil yanvar. Ideal holat.',
 'Yangi kabi', 'Toshkent, Chilonzor', 'Bor (xaridor tolaydi)',
 22000000, 300000, 23500000, 'active',
 NOW() - INTERVAL 1 DAY, NOW() + INTERVAL 4 DAY, TRUE, 220000),

(3, 6,
 'Oltin uzuk 14K 5.2 gramm',
 'Toshkentda yasalgan 14K oltin uzuk. Sertifikat bilan.',
 'Yangi', 'Toshkent', 'Faqat shaxsan topshirish',
 2800000, 50000, 3400000, 'active',
 NOW() - INTERVAL 1 DAY, NOW() + INTERVAL 2 DAY, TRUE, 28000),

(4, 2,
 'Chevrolet Cobalt 2022 18000 km',
 '2022-yil, oq rang, 18000 km yurgan. Bitta egasi. Hujjatlar tayyor.',
 'Yaxshi holat', 'Toshkent, Yakkasaroy', 'Kelishiladi',
 145000000, 1000000, 148000000, 'active',
 NOW() - INTERVAL 2 DAY, NOW() + INTERVAL 6 DAY, TRUE, 1450000),

(3, 6,
 'Kumush bilakuzuk handmade',
 'Uzbek ustasi tomonidan qolda yasalgan kumush bilakuzuk. 18 gramm.',
 'Yangi', 'Buxoro', 'Bor (xaridor tolaydi)',
 800000, 20000, 950000, 'active',
 NOW() - INTERVAL 2 DAY, NOW() + INTERVAL 30 MINUTE, TRUE, 8000),

(4, 1,
 'Sony PlayStation 5 Disc Edition',
 'Yangi, quti ochilmagan PS5. Bitta DualSense controller bilan.',
 'Yangi (quti ochilmagan)', 'Toshkent', 'Bor (xaridor tolaydi)',
 4500000, 100000, NULL, 'pending',
 NOW() + INTERVAL 1 DAY, NOW() + INTERVAL 4 DAY, TRUE, 45000),

(3, 1,
 'iPad Pro 12.9 dyuym M2 256GB WiFi',
 'Apple iPad Pro M2. Liquid Retina XDR display. Apple Pencil bilan.',
 'Yangi kabi', 'Toshkent', 'Bor (xaridor tolaydi)',
 9000000, 100000, 11500000, 'sold',
 NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 3 DAY, TRUE, 90000)

ON DUPLICATE KEY UPDATE title = VALUES(title);

-- Takliflar
INSERT INTO bids (auction_id, bidder_id, amount, created_at) VALUES
(1, 2, 8700000,  NOW() - INTERVAL 2 DAY),
(1, 5, 8900000,  NOW() - INTERVAL 30 HOUR),
(1, 2, 9100000,  NOW() - INTERVAL 1 DAY),
(1, 5, 9200000,  NOW() - INTERVAL 5 HOUR),
(2, 2, 3400000,  NOW() - INTERVAL 1 DAY),
(2, 5, 3700000,  NOW() - INTERVAL 12 HOUR),
(2, 2, 4100000,  NOW() - INTERVAL 3 HOUR),
(4, 5, 22500000, NOW() - INTERVAL 20 HOUR),
(4, 2, 23000000, NOW() - INTERVAL 10 HOUR),
(4, 5, 23500000, NOW() - INTERVAL 2 HOUR);

-- Qatnashchilar
INSERT INTO auction_participants (auction_id, user_id, fee_paid, joined_at) VALUES
(1, 2, TRUE, NOW() - INTERVAL 2 DAY),
(1, 5, TRUE, NOW() - INTERVAL 1 DAY),
(2, 2, TRUE, NOW() - INTERVAL 1 DAY),
(2, 5, TRUE, NOW() - INTERVAL 12 HOUR),
(4, 2, TRUE, NOW() - INTERVAL 1 DAY),
(4, 5, TRUE, NOW() - INTERVAL 20 HOUR)
ON DUPLICATE KEY UPDATE fee_paid = TRUE;

-- Tolovlar
INSERT INTO payments (user_id, auction_id, type, amount, status, method, description) VALUES
(3, 1, 'seller_fee',        85000,   'completed', 'payme', 'iPhone garov tolovi'),
(3, 2, 'seller_fee',        32000,   'completed', 'click', 'Gilam garov tolovi'),
(4, 3, 'seller_fee',        120000,  'completed', 'payme', 'Samsung TV garov tolovi'),
(2, 1, 'participation_fee', 50000,   'completed', 'payme', 'iPhone auktsioniga qatnashish'),
(5, 1, 'participation_fee', 50000,   'completed', 'click', 'iPhone auktsioniga qatnashish'),
(2, 2, 'participation_fee', 50000,   'completed', 'payme', 'Gilam auktsioniga qatnashish');

-- Bildirishnomalar
INSERT INTO notifications (user_id, type, title, message, is_read) VALUES
(2, 'outbid',  'Taklifingizdan otildi!',
 'iPhone auktsionida yangi taklif: 9 200 000 som', FALSE),
(5, 'outbid',  'Taklifingizdan otildi!',
 'MacBook Pro auktsionida yangi taklif: 23 500 000 som', FALSE),
(3, 'payment', 'Garov tolovi qabul qilindi',
 'iPhone auktsioningiz faollashtirildi', TRUE),
(2, 'winner',  'Tabriklaymiz! Siz golib boldingiz!',
 'iPad Pro auktsionida siz golib boldingiz 11 500 000 som', TRUE);

SELECT 'Seed muvaffaqiyatli yuklandi!' AS natija;
SELECT CONCAT('Foydalanuvchilar: ', COUNT(*)) AS info FROM users;
SELECT CONCAT('Auktsionlar: ',      COUNT(*)) AS info FROM auctions;
SELECT CONCAT('Takliflar: ',        COUNT(*)) AS info FROM bids;