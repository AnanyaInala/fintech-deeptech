-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
--  MySQL Setup Script - User Management (Redis vs MySQL)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- Step 1: Create the database (if it doesn't exist)
CREATE DATABASE IF NOT EXISTS MRUMRECW;

-- Step 2: Switch to the database
USE MRUMRECW;

-- Step 3: Create the users table
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    age         INT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_email (email)          -- Index for faster email lookups
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 4: (Optional) Seed with sample data for testing
-- Uncomment the block below to insert 10 sample users

/*
INSERT INTO users (name, email, age) VALUES
    ('Alice Johnson',   'alice@example.com',    28),
    ('Bob Smith',       'bob@example.com',      34),
    ('Charlie Brown',   'charlie@example.com',  22),
    ('Diana Prince',    'diana@example.com',    30),
    ('Edward Norton',   'edward@example.com',   45),
    ('Fiona Apple',     'fiona@example.com',    27),
    ('George Lucas',    'george@example.com',   51),
    ('Hannah Montana',  'hannah@example.com',   19),
    ('Ivan Drago',      'ivan@example.com',     38),
    ('Julia Roberts',   'julia@example.com',    42);
*/

-- Step 5: Verify the table was created
DESCRIBE users;

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
--  BULK DATA GENERATOR (for JMeter Performance Testing)
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- Run the procedure below to insert 500 users for performance comparison.

DELIMITER //

CREATE PROCEDURE IF NOT EXISTS generate_test_users(IN num_users INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    
    WHILE i <= num_users DO
        INSERT INTO users (name, email, age)
        VALUES (
            CONCAT('User_', i),
            CONCAT('user', i, '@test.com'),
            FLOOR(18 + RAND() * 50)    -- Random age between 18 and 67
        );
        SET i = i + 1;
    END WHILE;
END //

DELIMITER ;

-- Usage: CALL generate_test_users(500);
-- This creates 500 test users for benchmarking Redis vs MySQL performance.
