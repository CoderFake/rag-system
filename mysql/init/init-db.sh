#!/bin/bash
set -e

echo "Đang đợi MySQL khởi động hoàn toàn..."
until mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1"; do
  echo "MySQL chưa sẵn sàng - đang đợi..."
  sleep 2
done

echo "Đang khởi tạo database..."

mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" <<-EOSQL
    -- Tạo bảng users
    CREATE TABLE IF NOT EXISTS \`users\` (
        \`id\` INT AUTO_INCREMENT PRIMARY KEY,
        \`username\` VARCHAR(100) NOT NULL UNIQUE,
        \`password\` VARCHAR(255) NOT NULL,
        \`name\` VARCHAR(255),
        \`email\` VARCHAR(255),
        \`role\` VARCHAR(50) NOT NULL DEFAULT 'user',
        \`created_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        \`updated_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

    -- Tạo bảng documents
    CREATE TABLE IF NOT EXISTS \`documents\` (
        \`id\` VARCHAR(255) PRIMARY KEY,
        \`title\` VARCHAR(255) NOT NULL,
        \`file_path\` VARCHAR(255),
        \`file_type\` VARCHAR(50),
        \`category\` VARCHAR(100) DEFAULT 'general',
        \`user_id\` INT,
        \`created_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        \`updated_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (\`user_id\`) REFERENCES \`users\`(\`id\`) ON DELETE SET NULL
    );

    -- Tạo bảng document_tags
    CREATE TABLE IF NOT EXISTS \`document_tags\` (
        \`id\` INT AUTO_INCREMENT PRIMARY KEY,
        \`document_id\` VARCHAR(255),
        \`tag\` VARCHAR(100),
        FOREIGN KEY (\`document_id\`) REFERENCES \`documents\`(\`id\`) ON DELETE CASCADE,
        UNIQUE(\`document_id\`, \`tag\`)
    );

    -- Tạo bảng queries
    CREATE TABLE IF NOT EXISTS \`queries\` (
        \`id\` VARCHAR(36) PRIMARY KEY,
        \`text\` TEXT NOT NULL,
        \`user_id\` INT,
        \`session_id\` VARCHAR(100),
        \`language\` VARCHAR(10) DEFAULT 'vi',
        \`query_type\` VARCHAR(50) DEFAULT 'rag',
        \`enhanced_text\` TEXT,
        \`created_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (\`user_id\`) REFERENCES \`users\`(\`id\`) ON DELETE SET NULL
    );

    -- Tạo bảng responses
    CREATE TABLE IF NOT EXISTS \`responses\` (
        \`id\` VARCHAR(36) PRIMARY KEY,
        \`query_id\` VARCHAR(36) NOT NULL,
        \`text\` TEXT NOT NULL,
        \`query_text\` TEXT NOT NULL,
        \`response_type\` VARCHAR(50) DEFAULT 'rag',
        \`session_id\` VARCHAR(100),
        \`user_id\` INT,
        \`language\` VARCHAR(10) DEFAULT 'vi',
        \`processing_time\` FLOAT,
        \`created_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (\`query_id\`) REFERENCES \`queries\`(\`id\`) ON DELETE CASCADE,
        FOREIGN KEY (\`user_id\`) REFERENCES \`users\`(\`id\`) ON DELETE SET NULL
    );

    -- Tạo bảng response_sources
    CREATE TABLE IF NOT EXISTS \`response_sources\` (
        \`id\` INT AUTO_INCREMENT PRIMARY KEY,
        \`response_id\` VARCHAR(36) NOT NULL,
        \`document_id\` VARCHAR(255) NOT NULL,
        \`relevance_score\` FLOAT,
        FOREIGN KEY (\`response_id\`) REFERENCES \`responses\`(\`id\`) ON DELETE CASCADE,
        FOREIGN KEY (\`document_id\`) REFERENCES \`documents\`(\`id\`) ON DELETE CASCADE
    );

    -- Tạo bảng feedback
    CREATE TABLE IF NOT EXISTS \`feedback\` (
        \`id\` INT AUTO_INCREMENT PRIMARY KEY,
        \`response_id\` VARCHAR(36) NOT NULL,
        \`user_id\` INT,
        \`feedback_type\` VARCHAR(50) NOT NULL,
        \`value\` TEXT,
        \`created_at\` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (\`response_id\`) REFERENCES \`responses\`(\`id\`) ON DELETE CASCADE,
        FOREIGN KEY (\`user_id\`) REFERENCES \`users\`(\`id\`) ON DELETE SET NULL
    );
EOSQL


mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" <<-EOSQL
    -- Tạo tài khoản admin mặc định nếu chưa tồn tại
    -- Mật khẩu: admin123 (được hash bằng SHA-256)
    INSERT INTO \`users\` (\`username\`, \`password\`, \`name\`, \`role\`, \`created_at\`)
    SELECT 'admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrator', 'admin', NOW()
    FROM DUAL
    WHERE NOT EXISTS (SELECT 1 FROM \`users\` WHERE \`username\` = 'admin');
EOSQL

echo "Khởi tạo database hoàn tất!"