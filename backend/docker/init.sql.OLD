-- ============================================
-- Script SQL d'initialisation - Infolocale Scraper
-- Conforme au cahier des charges
-- ============================================

-- Extension pour PostgreSQL (si nécessaire)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Table: users
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    pseudo VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Email confirmation
    email_confirmed BOOLEAN DEFAULT FALSE,
    confirmation_token VARCHAR(255),
    confirmation_sent_at TIMESTAMP,

    -- Password reset
    reset_token VARCHAR(255),
    reset_sent_at TIMESTAMP,

    -- Device tracking
    device_id VARCHAR(255),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

-- Index sur email pour recherches rapides
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ============================================
-- Table: scanned_events
-- ============================================

CREATE TABLE IF NOT EXISTS scanned_events (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Key vers users
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Identifiant unique (déduplication)
    uid VARCHAR(100) UNIQUE NOT NULL,

    -- ===== CHAMPS PRINCIPAUX =====
    title VARCHAR(500) NOT NULL,
    category VARCHAR(255),

    -- Dates et heures
    begin_date DATE,
    end_date DATE,
    start_time VARCHAR(10),
    end_time VARCHAR(10),

    -- Contenu
    description TEXT,
    organizer VARCHAR(500),
    pricing VARCHAR(200),
    website VARCHAR(500),

    -- Arrays PostgreSQL
    tags TEXT[],
    artists TEXT[],
    sponsors TEXT[],

    -- ===== CHAMPS DE LOCALISATION =====
    location_name VARCHAR(500),
    address VARCHAR(500),
    zipcode VARCHAR(20),
    city VARCHAR(200),
    state VARCHAR(255),
    country VARCHAR(255),

    -- Coordonnées GPS (géocodage)
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    display_name VARCHAR(1000),

    -- ===== CHAMPS GOOGLE PLACES =====
    place_id VARCHAR(255),
    place_name VARCHAR(500),
    place_types TEXT[],
    rating DECIMAL(2,1),

    -- ===== CHAMPS TECHNIQUES =====
    image_path VARCHAR(500),
    qr_code TEXT,
    schema_org_types TEXT[],
    raw_json JSONB,

    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- Index requis (performance)
-- ============================================

-- Index sur user_id
CREATE INDEX IF NOT EXISTS idx_scanned_events_user ON scanned_events(user_id);

-- Index sur is_private
CREATE INDEX IF NOT EXISTS idx_scanned_events_private ON scanned_events(is_private);

-- Index composite sur latitude et longitude
CREATE INDEX IF NOT EXISTS idx_scanned_events_coords ON scanned_events(latitude, longitude);

-- Index sur uid pour déduplication rapide
CREATE INDEX IF NOT EXISTS idx_scanned_events_uid ON scanned_events(uid);

-- Index sur begin_date pour filtres temporels
CREATE INDEX IF NOT EXISTS idx_scanned_events_begin_date ON scanned_events(begin_date);

-- Index sur city pour recherches géographiques
CREATE INDEX IF NOT EXISTS idx_scanned_events_city ON scanned_events(city);

-- Index sur category pour filtres
CREATE INDEX IF NOT EXISTS idx_scanned_events_category ON scanned_events(category);

-- Index GIN sur raw_json pour requêtes JSON
CREATE INDEX IF NOT EXISTS idx_scanned_events_raw_json ON scanned_events USING GIN(raw_json);

-- ============================================
-- Insertion d'un utilisateur par défaut
-- ============================================

INSERT INTO users (id, pseudo, email, password_hash, email_confirmed, created_at)
VALUES (
    1,
    'scraper_bot',
    'scraper@infolocale.local',
    -- Hash bcrypt du mot de passe "changeme" (à changer en production)
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5MAntAOzdw1jW',
    TRUE,
    NOW()
)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- Commentaires sur les tables
-- ============================================

COMMENT ON TABLE users IS 'Table des utilisateurs du système';
COMMENT ON TABLE scanned_events IS 'Table des événements scrapés depuis Infolocale.fr';

COMMENT ON COLUMN scanned_events.uid IS 'Identifiant unique pour déduplication';
COMMENT ON COLUMN scanned_events.raw_json IS 'Données brutes JSON complètes de l''événement';
COMMENT ON COLUMN scanned_events.latitude IS 'Latitude GPS obtenue via géocodage Google Places';
COMMENT ON COLUMN scanned_events.longitude IS 'Longitude GPS obtenue via géocodage Google Places';
COMMENT ON COLUMN scanned_events.place_id IS 'Identifiant Google Places du lieu';
COMMENT ON COLUMN scanned_events.rating IS 'Note Google Places (0.0 à 5.0)';

-- ============================================
-- Vue pour statistiques
-- ============================================

CREATE OR REPLACE VIEW v_event_stats AS
SELECT
    COUNT(*) as total_events,
    COUNT(DISTINCT city) as total_cities,
    COUNT(DISTINCT category) as total_categories,
    COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded_events,
    COUNT(CASE WHEN is_private = TRUE THEN 1 END) as private_events,
    MIN(begin_date) as earliest_event,
    MAX(begin_date) as latest_event
FROM scanned_events;

-- ============================================
-- Fonction pour nettoyer les événements anciens
-- ============================================

CREATE OR REPLACE FUNCTION cleanup_old_events(days_old INTEGER DEFAULT 365)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM scanned_events
    WHERE begin_date < NOW() - (days_old || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_old_events IS 'Supprimer les événements plus anciens que X jours (défaut: 365)';

-- ============================================
-- Fin du script d'initialisation
-- ============================================
