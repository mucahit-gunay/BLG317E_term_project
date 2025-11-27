-- MySQL Veritabanı Kurulum Scripti
-- Bu dosyayı MySQL'de çalıştırarak veritabanını oluşturabilirsiniz

-- 1. Veritabanını oluştur
CREATE DATABASE IF NOT EXISTS tesseract CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Kullanıcı oluştur (eğer yoksa)
-- NOT: Eğer kullanıcı zaten varsa, sadece şifresini güncellemek için:
-- ALTER USER 'tesseract'@'localhost' IDENTIFIED BY 'Zarif123.Bb';

CREATE USER IF NOT EXISTS 'tesseract'@'localhost' IDENTIFIED BY 'Zarif123.Bb';

-- 3. Kullanıcıya yetkileri ver
GRANT ALL PRIVILEGES ON tesseract.* TO 'tesseract'@'localhost';
FLUSH PRIVILEGES;

-- 4. Veritabanını kullan
USE tesseract;

-- 5. Tabloları oluştur

-- 1. AGENCY Table
CREATE TABLE IF NOT EXISTS agency (
    agency_id INTEGER PRIMARY KEY,
    agency_name VARCHAR(255) NOT NULL,
    agency_url VARCHAR(255) NOT NULL,
    agency_timezone VARCHAR(100) NOT NULL,
    agency_lang VARCHAR(10) NOT NULL,
    agency_phone VARCHAR(50) NULL,
    agency_fare_url VARCHAR(500) NULL,
    agency_email VARCHAR(255) NULL
);

-- 2. STOPS Table
CREATE TABLE IF NOT EXISTS stops (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    stop_id INTEGER UNIQUE NOT NULL,
    stop_code VARCHAR(100),
    stop_name VARCHAR(255),
    stop_desc VARCHAR(255),
    stop_lat DECIMAL(10, 8),
    stop_lon DECIMAL(11, 8),
    zone_id INTEGER NULL,
    stop_url VARCHAR(255) NULL,
    location_type SMALLINT,
    parent_station VARCHAR(255) NULL,
    stop_timezone VARCHAR(100) NULL,
    wheelchair_boarding SMALLINT,
    boarding SMALLINT NULL
);

-- 3. ROUTES TABLE
CREATE TABLE IF NOT EXISTS routes (
    route_id VARCHAR(255) PRIMARY KEY,
    agency_id INTEGER,
    route_short_name VARCHAR(100),
    route_long_name TEXT,
    route_desc TEXT,
    route_type INT,
    route_url TEXT,
    route_color VARCHAR(10),
    route_text_color VARCHAR(10),
    FOREIGN KEY (agency_id) REFERENCES agency(agency_id) ON DELETE SET NULL
);

-- 4. CALENDAR TABLE
CREATE TABLE IF NOT EXISTS calendar (
    service_id VARCHAR(255) PRIMARY KEY,
    monday VARCHAR(1) NOT NULL CHECK (monday IN ('0', '1')),
    tuesday VARCHAR(1) NOT NULL CHECK (tuesday IN ('0', '1')),
    wednesday VARCHAR(1) NOT NULL CHECK (wednesday IN ('0', '1')),
    thursday VARCHAR(1) NOT NULL CHECK (thursday IN ('0', '1')),
    friday VARCHAR(1) NOT NULL CHECK (friday IN ('0', '1')),
    saturday VARCHAR(1) NOT NULL CHECK (saturday IN ('0', '1')),
    sunday VARCHAR(1) NOT NULL CHECK (sunday IN ('0', '1')),
    start_date VARCHAR(8) NOT NULL,
    end_date VARCHAR(8) NOT NULL
);

-- 5. TRIPS TABLE
CREATE TABLE IF NOT EXISTS trips (
    _id INTEGER PRIMARY KEY AUTO_INCREMENT,
    route_id VARCHAR(255),
    service_id VARCHAR(255),
    trip_id INTEGER UNIQUE NOT NULL,
    trip_headsign VARCHAR(255),
    trip_short_name VARCHAR(100),
    direction_id SMALLINT,
    block_id VARCHAR(255),
    shape_id INTEGER,
    wheelchair_accessible SMALLINT,
    bikes_allowed SMALLINT,
    start_time TIME,
    FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES calendar(service_id) ON DELETE SET NULL
);

-- 6. STOP_TIMES TABLE
CREATE TABLE IF NOT EXISTS stop_times (
    trip_id INTEGER NOT NULL,
    arrival_time TIME NOT NULL,
    departure_time TIME NOT NULL,
    stop_id INTEGER NOT NULL,
    stop_sequence INTEGER NOT NULL,
    stop_headsign VARCHAR(255) NULL,
    pickup_type SMALLINT,
    drop_off_type SMALLINT,
    shape_dist_traveled DECIMAL(10, 5) NULL,
    timepoint SMALLINT,
    PRIMARY KEY (trip_id, stop_sequence),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE,
    FOREIGN KEY (stop_id) REFERENCES stops(stop_id) ON DELETE CASCADE
);

-- 7. SHAPES TABLE
CREATE TABLE IF NOT EXISTS shapes (
    shape_id INTEGER NOT NULL,
    shape_pt_lat DECIMAL(16, 13) NOT NULL,
    shape_pt_lon DECIMAL(16, 13) NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    shape_dist_traveled DECIMAL(10, 5) NULL,
    PRIMARY KEY (shape_id, shape_pt_sequence)
);

-- 8. FREQUENCIES TABLE
CREATE TABLE IF NOT EXISTS frequencies (
    trip_id INTEGER,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    headway_secs INT,
    exact_times INT,
    PRIMARY KEY (trip_id, start_time),
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id) ON DELETE CASCADE
);

-- Başarı mesajı
SELECT 'Veritabanı ve tablolar başarıyla oluşturuldu!' AS Status;

