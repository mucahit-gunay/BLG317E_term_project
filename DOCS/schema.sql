--Mehmet Elhan Table 1
-- 1. AGENCY Table
CREATE TABLE agency (
    agency_id INTEGER PRIMARY KEY,
    agency_name VARCHAR(255) NOT NULL,
    agency_url VARCHAR(255) NOT NULL,
    agency_timezone VARCHAR(100) NOT NULL,
    agency_lang VARCHAR(10) NOT NULL,
    agency_phone VARCHAR(50) NULL,
    agency_fare_url VARCHAR(500) NULL,
    agency_email VARCHAR(255) NULL
);

--Mehmet Elhan Table 2
-- 2. STOPS Table

CREATE TABLE stops (
    id INTEGER PRIMARY KEY,
    stop_id INTEGER UNIQUE NOTNULL,
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
CREATE TABLE routes (
    route_id VARCHAR(255) PRIMARY KEY,
    agency_id VARCHAR(255) REFERENCES agency(agency_id),
    route_short_name VARCHAR(100),
    route_long_name TEXT,
    route_desc TEXT,
    route_type INT,
    route_url TEXT,
    route_color VARCHAR(10),
    route_text_color VARCHAR(10)
);

-- 4. FREQUENCIES TABLE
CREATE TABLE frequencies (
    trip_id VARCHAR(255) REFERENCES trips(trip_id),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    headway_secs INT,
    exact_times INT,
    PRIMARY KEY (trip_id, start_time)
);

-- Mucahit Table 1
-- 5. TRIPS TABLe
CREATE TABLE trips (
    _id INTEGER PRIMARY KEY,
    route_id INTEGER,
    service_id INTEGER,
    trip_id INTEGER UNIQUE NOT NULL,
    trip_headsign VARCHAR(255),
    trip_short_name VARCHAR(100),
    direction_id SMALLINT,
    block_id VARCHAR(255),
    shape_id INTEGER,
    wheelchair_accessible SMALLINT,
    bikes_allowed SMALLINT,
    PRIMARY KEY (trip_id),
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
    ON DELETE CASCADE
);

-- Mucahit Table 2
-- 6. CALENDAR TABLE
CREATE TABLE calendar (
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

--Talha table 1
--7. STOP_TIMES TABLE
CREATE TABLE stop_times (
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

    -- Birincil anahtarı (PRIMARY KEY) iki sütunun kombinasyonu olarak tanımlıyoruz:
    PRIMARY KEY (trip_id, stop_sequence)
);
--Talha table 2
--8.SHAPES TABLE
CREATE TABLE shapes (
    shape_id INTEGER NOT NULL,
    shape_pt_lat DECIMAL(16, 13) NOT NULL,
    shape_pt_lon DECIMAL(16, 13) NOT NULL,
    shape_pt_sequence INTEGER NOT NULL,
    shape_dist_traveled DECIMAL(10, 5) NULL,

    -- Birincil anahtar, shape_id ve o hattaki noktanın sırasıdır:
    PRIMARY KEY (shape_id, shape_pt_sequence)
);