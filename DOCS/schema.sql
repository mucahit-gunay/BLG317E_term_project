-- 1. AGENCY Table

CREATE TABLE agency (
    agency_id VARCHAR(255) PRIMARY KEY,
    agency_name VARCHAR(255) NOT NULL,
    agency_url TEXT,
    agency_timezone VARCHAR(100),
    agency_lang VARCHAR(10)
);


-- 2. ROUTES TABLE
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

-- Mucahit Table 1
-- 3. TRIPS TABLe
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

-- 4. FREQUENCIES TABLE
CREATE TABLE frequencies (
    trip_id VARCHAR(255) REFERENCES trips(trip_id),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    headway_secs INT,
    exact_times INT,
    PRIMARY KEY (trip_id, start_time)
);