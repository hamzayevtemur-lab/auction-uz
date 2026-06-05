CREATE DATABASE IF NOT EXISTS auction_uz CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE auction_uz;

CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    full_name   VARCHAR(100)  NOT NULL,
    email       VARCHAR(150)  NOT NULL UNIQUE,
    phone       VARCHAR(20)   NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,
    role        ENUM('buyer','seller','admin') DEFAULT 'buyer',
    balance     DECIMAL(15,2) DEFAULT 0.00,
    is_verified BOOLEAN       DEFAULT FALSE,
    is_active   BOOLEAN       DEFAULT TRUE,
    avatar_url  VARCHAR(255)  DEFAULT NULL,
    created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name_uz VARCHAR(100) NOT NULL,
    name_ru VARCHAR(100) DEFAULT NULL,
    icon    VARCHAR(50)  DEFAULT NULL,
    slug    VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS auctions (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    seller_id         INT           NOT NULL,
    category_id       INT           NOT NULL,
    title             VARCHAR(200)  NOT NULL,
    description       TEXT          DEFAULT NULL,
    item_condition    VARCHAR(100)  DEFAULT NULL,
    location          VARCHAR(100)  DEFAULT NULL,
    delivery          VARCHAR(100)  DEFAULT NULL,
    images            JSON          DEFAULT NULL,
    starting_price    DECIMAL(15,2) NOT NULL,
    reserve_price     DECIMAL(15,2) DEFAULT NULL,
    min_step          DECIMAL(15,2) DEFAULT 10000,
    current_bid       DECIMAL(15,2) DEFAULT NULL,
    winner_id         INT           DEFAULT NULL,
    status            ENUM('draft','pending','active','ended','cancelled','sold') DEFAULT 'draft',
    starts_at         DATETIME      NOT NULL,
    ends_at           DATETIME      NOT NULL,
    seller_fee_paid   BOOLEAN       DEFAULT FALSE,
    seller_fee_amount DECIMAL(15,2) DEFAULT NULL,
    created_at        DATETIME      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id)   REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (winner_id)   REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS bids (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    auction_id INT           NOT NULL,
    bidder_id  INT           NOT NULL,
    amount     DECIMAL(15,2) NOT NULL,
    is_winner  BOOLEAN       DEFAULT FALSE,
    created_at DATETIME      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (bidder_id)  REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT           NOT NULL,
    auction_id     INT           DEFAULT NULL,
    type           ENUM('seller_fee','participation_fee','escrow','payout','refund') NOT NULL,
    amount         DECIMAL(15,2) NOT NULL,
    status         ENUM('pending','completed','failed','refunded') DEFAULT 'pending',
    method         ENUM('payme','click','uzcard','balance') DEFAULT 'payme',
    transaction_id VARCHAR(255)  DEFAULT NULL,
    description    VARCHAR(255)  DEFAULT NULL,
    created_at     DATETIME      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id),
    FOREIGN KEY (auction_id) REFERENCES auctions(id)
);

CREATE TABLE IF NOT EXISTS auction_participants (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    auction_id INT      NOT NULL,
    user_id    INT      NOT NULL,
    fee_paid   BOOLEAN  DEFAULT FALSE,
    payment_id INT      DEFAULT NULL,
    joined_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_participant (auction_id, user_id),
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (user_id)    REFERENCES users(id),
    FOREIGN KEY (payment_id) REFERENCES payments(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT          NOT NULL,
    type       ENUM('outbid','winner','payment','auction_start','auction_end') NOT NULL,
    title      VARCHAR(200) NOT NULL,
    message    VARCHAR(500) DEFAULT NULL,
    is_read    BOOLEAN      DEFAULT FALSE,
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_auctions_status  ON auctions(status);
CREATE INDEX idx_auctions_ends_at ON auctions(ends_at);
CREATE INDEX idx_bids_auction     ON bids(auction_id);
CREATE INDEX idx_bids_bidder      ON bids(bidder_id);
CREATE INDEX idx_payments_user    ON payments(user_id);
CREATE INDEX idx_notif_user       ON notifications(user_id, is_read);
