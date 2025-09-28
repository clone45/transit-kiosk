-- Initial database schema for Transit Kiosk system

-- Stations table
CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Transit cards table
CREATE TABLE IF NOT EXISTS transit_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT UNIQUE NOT NULL,
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    usage_count INTEGER NOT NULL DEFAULT 0
);

-- Trips table
CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    completion_time TIMESTAMP,
    source_station_id INTEGER NOT NULL,
    destination_station_id INTEGER,
    cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    status TEXT NOT NULL DEFAULT 'active',
    FOREIGN KEY (card_id) REFERENCES transit_cards (id),
    FOREIGN KEY (source_station_id) REFERENCES stations (id),
    FOREIGN KEY (destination_station_id) REFERENCES stations (id)
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    transaction_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    previous_balance DECIMAL(10, 2) NOT NULL,
    new_balance DECIMAL(10, 2) NOT NULL,
    station_id INTEGER,
    FOREIGN KEY (card_id) REFERENCES transit_cards (id),
    FOREIGN KEY (station_id) REFERENCES stations (id)
);

-- Pricing table
CREATE TABLE IF NOT EXISTS pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_a_id INTEGER NOT NULL,
    station_b_id INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (station_a_id) REFERENCES stations (id),
    FOREIGN KEY (station_b_id) REFERENCES stations (id),
    UNIQUE(station_a_id, station_b_id)
);

-- API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP NULL,
    usage_count INTEGER DEFAULT 0
);