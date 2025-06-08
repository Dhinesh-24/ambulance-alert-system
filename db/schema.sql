-- Database schema for Ambulance Tracker System

CREATE DATABASE IF NOT EXISTS ambulance_db;
USE ambulance_db;

-- Users table (for regular users)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Drivers table (for ambulance drivers)
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    license_number VARCHAR(50),
    ambulance_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Driver locations table (stores real-time positions)
CREATE TABLE IF NOT EXISTS driver_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_id INT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE CASCADE,
    UNIQUE KEY (driver_id)
);

-- Hospitals table (for nearest hospital lookup)
CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    contact_number VARCHAR(20) NOT NULL
);

-- Emergency alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    driver_id INT,
    alert_type ENUM('police', 'hospital', 'general') NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
);

-- Sample hospital data (Chennai hospitals)
INSERT INTO hospitals (name, address, latitude, longitude, contact_number) VALUES
    ('Apollo Hospitals', '21 Greams Lane, Off Greams Road, Chennai', 13.067439, 80.262444, '+914428290000'),
    ('Fortis Malar Hospital', '52, 1st Main Road, Gandhi Nagar, Adyar, Chennai', 13.006752, 80.253613, '+914424944444'),
    ('MIOT International', '4/112, Mount Poonamallee Road, Manapakkam, Chennai', 13.010899, 80.178658, '+914422244222');

-- Create indexes for performance
CREATE INDEX idx_driver_locations ON driver_locations (driver_id);
CREATE INDEX idx_hospitals_location ON hospitals (latitude, longitude);