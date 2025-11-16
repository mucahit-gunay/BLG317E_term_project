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

