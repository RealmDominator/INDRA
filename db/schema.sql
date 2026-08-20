-- =============================================================================
-- INDRA — Database Schema (PostgreSQL 16)
-- =============================================================================
-- STATUS: PLANNED — This DDL is ready for execution but has NOT been applied.
-- See docs/05-database/DATABASE_SCHEMA.md for design rationale.
--
-- Source: PETRAS Analysis §9; INDRA Master Report §13
-- =============================================================================

-- Enable extensions (run once)
-- CREATE EXTENSION IF NOT EXISTS postgis;        -- Geospatial queries
-- CREATE EXTENSION IF NOT EXISTS timescaledb;    -- Time-series (optional)

-- =============================================================================
-- CORE REFERENCE ENTITIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    iso3 CHAR(3) UNIQUE,
    base_risk_score DECIMAL(5,3),
    region VARCHAR(50),
    is_hormuz_dependent BOOLEAN DEFAULT FALSE,
    is_red_sea_dependent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country_id INT REFERENCES countries(id),
    crude_grades TEXT[],
    annual_supply_capacity_mmtpa DECIMAL(8,2),
    current_sanctions_risk DECIMAL(5,3),
    is_sanctioned BOOLEAN DEFAULT FALSE,
    sanction_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    un_locode VARCHAR(10),
    country_id INT REFERENCES countries(id),
    is_indian BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    annual_crude_throughput_mmtpa DECIMAL(8,2),
    current_operational_status VARCHAR(20) DEFAULT 'OPERATIONAL',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS refineries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    owner VARCHAR(100),
    state VARCHAR(100),
    port_id INT REFERENCES ports(id),
    capacity_mmtpa DECIMAL(8,2),
    throughput_current_mmtpa DECIMAL(8,2),
    compatible_crude_grades TEXT[],
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    origin_port_id INT REFERENCES ports(id),
    dest_port_id INT REFERENCES ports(id),
    distance_nm INT,
    avg_transit_days DECIMAL(5,2),
    passes_through_hormuz BOOLEAN DEFAULT FALSE,
    passes_through_red_sea BOOLEAN DEFAULT FALSE,
    passes_through_malacca BOOLEAN DEFAULT FALSE,
    passes_through_cape BOOLEAN DEFAULT FALSE,
    base_freight_rate_per_mt DECIMAL(8,2),
    current_risk_score DECIMAL(5,3),
    is_operational BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- EVENT AND RISK TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS geopolitical_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,
    source_name VARCHAR(100),
    country_id INT REFERENCES countries(id),
    affected_route_ids INT[],
    severity DECIMAL(5,3),
    confidence DECIMAL(5,3),
    occurred_at TIMESTAMP,
    detected_at TIMESTAMP DEFAULT NOW(),
    is_verified BOOLEAN DEFAULT FALSE,
    raw_text TEXT,
    llm_model_used VARCHAR(100),
    is_simulated BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20),
    entity_id INT NOT NULL,
    score DECIMAL(5,3) NOT NULL,
    component_scores JSONB,
    contributing_event_ids INT[],
    calculated_at TIMESTAMP DEFAULT NOW(),
    valid_until TIMESTAMP,
    source VARCHAR(50),
    confidence DECIMAL(5,3)
);

-- =============================================================================
-- MARKET DATA TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS crude_prices (
    id SERIAL PRIMARY KEY,
    grade_name VARCHAR(100),
    price_usd_per_barrel DECIMAL(10,4),
    recorded_at TIMESTAMP,
    source VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS price_history (
    time TIMESTAMP NOT NULL,
    grade_name VARCHAR(100),
    price_usd_per_barrel DECIMAL(10,4),
    usd_inr_rate DECIMAL(10,4),
    price_inr_per_barrel DECIMAL(12,4)
        GENERATED ALWAYS AS (price_usd_per_barrel * usd_inr_rate) STORED
);

-- =============================================================================
-- SCENARIO AND OUTPUT TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    scenario_type VARCHAR(50),
    parameters JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id SERIAL PRIMARY KEY,
    scenario_id INT REFERENCES scenarios(id),
    affected_routes JSONB,
    supply_gap_mmt DECIMAL(8,3),
    price_impact_usd_per_barrel DECIMAL(8,4),
    reserve_drawdown_days DECIMAL(8,2),
    gdp_impact_estimate_usd_bn DECIMAL(10,3),
    freight_cost_increase_pct DECIMAL(8,2),
    recommendations JSONB,
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS procurement_options (
    id SERIAL PRIMARY KEY,
    scenario_id INT,
    refinery_id INT REFERENCES refineries(id),
    supplier_id INT REFERENCES suppliers(id),
    route_id INT REFERENCES routes(id),
    crude_grade VARCHAR(100),
    volume_available_mmt DECIMAL(8,3),
    price_cif_usd_per_barrel DECIMAL(10,4),
    transit_days DECIMAL(5,2),
    risk_score DECIMAL(5,3),
    compatibility VARCHAR(10),
    is_sanctioned BOOLEAN DEFAULT FALSE,
    ranking_score DECIMAL(10,6),
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS strategic_reserves (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(200),
    operator VARCHAR(100),
    state VARCHAR(100),
    capacity_mmt DECIMAL(8,3),
    current_level_mmt DECIMAL(8,3),
    days_coverage DECIMAL(8,2)
        GENERATED ALWAYS AS (current_level_mmt / 0.56) STORED,
    last_updated TIMESTAMP DEFAULT NOW(),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    data_classification VARCHAR(20) DEFAULT 'HISTORICAL'
);

-- =============================================================================
-- DATA SOURCE TRACKING
-- =============================================================================

CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT,
    update_frequency VARCHAR(50),
    last_fetched_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    classification VARCHAR(20)
);

-- =============================================================================
-- INDEXES (to be added during implementation)
-- =============================================================================

-- CREATE INDEX idx_events_detected_at ON geopolitical_events(detected_at DESC);
-- CREATE INDEX idx_events_type ON geopolitical_events(event_type);
-- CREATE INDEX idx_risk_scores_entity ON risk_scores(entity_type, entity_id);
-- CREATE INDEX idx_risk_scores_calculated ON risk_scores(calculated_at DESC);
-- CREATE INDEX idx_crude_prices_recorded ON crude_prices(recorded_at DESC);
-- CREATE INDEX idx_price_history_time ON price_history(time DESC);
