-- =============================================================================
-- INDRA — Database Schema (PostgreSQL 16)
-- =============================================================================
-- STATUS: RECONCILED with frozen DATABASE_SCHEMA.md (Step 4, 21 August 2026)
-- See docs/05-database/DATABASE_SCHEMA.md for design rationale.
--
-- Source: PETRAS Analysis §9; INDRA Master Report §13
-- Frozen: Step 2 Architecture Freeze (20 August 2026)
-- =============================================================================

-- =============================================================================
-- CORE REFERENCE ENTITIES
-- =============================================================================

CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    iso3 CHAR(3) UNIQUE,
    base_risk_score DECIMAL(5,3),               -- Internal scale 0.0–1.0
    region VARCHAR(50),                          -- Middle East, Africa, Americas, etc.
    is_hormuz_dependent BOOLEAN DEFAULT FALSE,   -- Does export route transit Hormuz?
    is_red_sea_dependent BOOLEAN DEFAULT FALSE,  -- Does export route transit Red Sea?
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS corridors (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,            -- Stable identifier: HORMUZ, RED_SEA, RUSSIA, SUEZ, MALACCA, CAPE
    name VARCHAR(200) NOT NULL,                  -- Human-readable: "Strait of Hormuz"
    description TEXT,                            -- Strategic significance description
    corridor_type VARCHAR(30),                   -- CHOKEPOINT, REGIONAL, SUPPLIER_CORRIDOR
    affected_countries TEXT[],                    -- Countries whose supply transits or depends on this corridor
    base_risk_score DECIMAL(5,3),                -- Baseline geopolitical risk (0.0–1.0 internal)
    india_dependency_share DECIMAL(5,3),         -- Fraction of India's imports affected (e.g., 0.42 for Hormuz)
    is_active BOOLEAN DEFAULT TRUE,              -- Can be deactivated for scenarios
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS crude_grades (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,           -- Canonical name: "Arab Light", "Urals", "Basrah Light"
    api_gravity DECIMAL(5,2),                    -- Degrees API (light/heavy indicator)
    sulfur_content_pct DECIMAL(5,3),             -- Sulfur % (sweet/sour indicator)
    category VARCHAR(20),                        -- LIGHT_SWEET, LIGHT_SOUR, MEDIUM_SOUR, HEAVY_SOUR
    origin_country_id INT REFERENCES countries(id), -- Primary producing country
    notes TEXT                                   -- Source/assumptions for data
);

CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    country_id INT REFERENCES countries(id),
    crude_grade_ids INT[],                       -- FK references to crude_grades table
    annual_supply_capacity_mmtpa DECIMAL(8,2),
    current_sanctions_risk DECIMAL(5,3),         -- Internal 0.0–1.0
    is_sanctioned BOOLEAN DEFAULT FALSE,
    sanction_source VARCHAR(50),                 -- OFAC, EU, UN, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    un_locode VARCHAR(10),                       -- UN/LOCODE identifier
    country_id INT REFERENCES countries(id),
    is_indian BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    annual_crude_throughput_mmtpa DECIMAL(8,2),
    current_operational_status VARCHAR(20) DEFAULT 'OPERATIONAL', -- OPERATIONAL, DISRUPTED, CLOSED
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS refineries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    owner VARCHAR(100),                          -- IOC, BPCL, HPCL, Reliance, etc.
    state VARCHAR(100),                          -- Indian state
    port_id INT REFERENCES ports(id),            -- Nearest receiving port
    capacity_mmtpa DECIMAL(8,2),                 -- Annual capacity
    throughput_current_mmtpa DECIMAL(8,2),       -- Current operating throughput
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- NOTE: Crude compatibility is modeled via refinery_supply_mix, not TEXT[] arrays.

CREATE TABLE IF NOT EXISTS refinery_supply_mix (
    id SERIAL PRIMARY KEY,
    refinery_id INT REFERENCES refineries(id) NOT NULL,
    crude_grade_id INT REFERENCES crude_grades(id) NOT NULL,
    compatibility VARCHAR(10) NOT NULL,          -- HIGH, MEDIUM, LOW, NONE
    compatibility_score DECIMAL(3,2),            -- Numeric: 0.0–1.0 (where 1.0 = fully compatible)
    current_share_pct DECIMAL(5,2),              -- Current % of refinery intake from this grade. NULL if unknown
    max_share_pct DECIMAL(5,2),                  -- Maximum processable % of this grade. NULL if unknown
    source_type VARCHAR(30),                     -- PPAC_REPORTED, COMPANY_REPORT, ESTIMATED, UNKNOWN
    notes TEXT,                                  -- Assumptions, caveats
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(refinery_id, crude_grade_id)           -- One row per refinery-grade combination
);

CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,                  -- Descriptive route name
    origin_port_id INT REFERENCES ports(id),
    dest_port_id INT REFERENCES ports(id),
    corridor_ids INT[],                          -- FK references to corridors table — which corridors this route transits
    distance_nm INT,                             -- Distance in nautical miles
    avg_transit_days DECIMAL(5,2),
    base_freight_rate_per_mt DECIMAL(8,2),
    current_risk_score DECIMAL(5,3),             -- Internal 0.0–1.0
    is_operational BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- EVENT AND RISK TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS geopolitical_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),                      -- SANCTION, MILITARY, PORT_CLOSURE, ATTACK, DIPLOMATIC, OTHER
    title TEXT NOT NULL,
    description TEXT,
    source_url TEXT,                              -- Original source URL
    source_name VARCHAR(100),                    -- GDELT, ACLED, OFAC, RSS, etc.
    affected_country_ids INT[],                  -- FK refs → countries. Supports multiple countries per event
    affected_corridor_ids INT[],                 -- FK refs → corridors. Which corridors are affected
    affected_route_ids INT[],                    -- FK refs → routes. Specific routes if identified
    severity DECIMAL(5,3),                       -- Internal 0.0–1.0
    confidence DECIMAL(5,3),                     -- LLM extraction confidence, 0.0–1.0
    occurred_at TIMESTAMP,                       -- When the event happened
    detected_at TIMESTAMP DEFAULT NOW(),         -- When INDRA ingested it
    is_verified BOOLEAN DEFAULT FALSE,           -- Cross-source verification
    raw_text TEXT,                               -- Original article text (truncated for storage)
    llm_model_used VARCHAR(100),                 -- Which LLM extracted this event
    is_simulated BOOLEAN DEFAULT FALSE           -- Is this a demo fixture?
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20),                     -- corridor, route, supplier, country
    entity_id INT NOT NULL,                      -- References the entity
    score DECIMAL(5,3) NOT NULL,                 -- Internal 0.0–1.0
    risk_level VARCHAR(10),                      -- LOW, MODERATE, HIGH, CRITICAL, EXTREME
    component_scores JSONB,                      -- Full breakdown of scoring components (all in 0.0–1.0)
    contributing_event_ids INT[],                -- Events that contributed to this score
    calculated_at TIMESTAMP DEFAULT NOW(),
    valid_until TIMESTAMP,                       -- Score expiration
    calculation_method VARCHAR(50),              -- "weighted_rule_v1", "xgboost_v1", etc.
    confidence DECIMAL(5,3)                      -- 0.0–1.0
);

-- =============================================================================
-- MARKET DATA TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS commodity_prices (
    id SERIAL PRIMARY KEY,
    grade_name VARCHAR(100),                     -- Brent, WTI, Dubai, Urals, etc.
    crude_grade_id INT REFERENCES crude_grades(id), -- NULL for benchmark grades not in crude_grades table
    price_usd_per_barrel DECIMAL(10,4) NOT NULL,
    source VARCHAR(50) NOT NULL,                 -- EIA, World Bank, etc.
    source_timestamp TIMESTAMP,                  -- When the source published this price
    observed_at TIMESTAMP DEFAULT NOW(),         -- When INDRA recorded it
    data_semantic VARCHAR(30) DEFAULT 'OBSERVED' -- OBSERVED, HISTORICAL
);

CREATE TABLE IF NOT EXISTS fx_rates (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) NOT NULL,           -- "USD_INR"
    rate DECIMAL(10,4) NOT NULL,
    source VARCHAR(50) NOT NULL,                  -- RBI, etc.
    source_timestamp TIMESTAMP,                   -- When the source published this rate
    observed_at TIMESTAMP DEFAULT NOW(),          -- When INDRA recorded it
    data_semantic VARCHAR(30) DEFAULT 'OBSERVED'  -- OBSERVED, HISTORICAL
);

-- =============================================================================
-- SCENARIO AND OUTPUT TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS scenarios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    scenario_type VARCHAR(50),                   -- HORMUZ_FULL, HORMUZ_PARTIAL, RUSSIA_LOSS, RED_SEA, PRICE_SPIKE
    parameters JSONB,                            -- All scenario parameters
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS scenario_results (
    id SERIAL PRIMARY KEY,
    scenario_id INT REFERENCES scenarios(id) NOT NULL,
    affected_corridors JSONB,                    -- Which corridors are disrupted and how
    affected_routes JSONB,                       -- Which routes are affected
    supply_gap_mmt DECIMAL(8,3),
    price_impact_usd_per_barrel DECIMAL(8,4),
    freight_cost_increase_pct DECIMAL(8,2),
    spr_bridge JSONB,                            -- { required_mmt, available_mmt, days_bridged, uncovered_gap_mmt }
    affected_refineries JSONB,                   -- Per-refinery impact breakdown
    assumptions JSONB,                           -- All assumptions used, with data_semantic tags
    calculated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS procurement_options (
    id SERIAL PRIMARY KEY,
    scenario_id INT REFERENCES scenarios(id) NOT NULL,  -- Context scenario
    refinery_id INT REFERENCES refineries(id) NOT NULL,  -- Target refinery
    supplier_id INT REFERENCES suppliers(id),
    route_id INT REFERENCES routes(id),
    crude_grade_id INT REFERENCES crude_grades(id),
    volume_available_mmt DECIMAL(8,3),
    price_cif_usd_per_barrel DECIMAL(10,4),
    transit_days DECIMAL(5,2),
    risk_score DECIMAL(5,3),                     -- Internal 0.0–1.0
    compatibility VARCHAR(10),                   -- HIGH, MEDIUM, LOW
    is_sanctioned BOOLEAN DEFAULT FALSE,
    ranking_score DECIMAL(10,6),                 -- Composite ranking score
    scoring_breakdown JSONB,                     -- Component scores used in ranking
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS strategic_reserves (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(200),
    operator VARCHAR(100),                       -- ISPRL
    state VARCHAR(100),                          -- Indian state
    capacity_mmt DECIMAL(8,3),
    current_level_mmt DECIMAL(8,3),              -- Estimated
    last_updated TIMESTAMP DEFAULT NOW(),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    data_classification VARCHAR(20) DEFAULT 'HISTORICAL' -- HISTORICAL, ESTIMATED
);

-- days_coverage is computed at application/query layer:
-- days_coverage = current_level_mmt / india_daily_consumption_mmt

-- =============================================================================
-- PROVENANCE / EVIDENCE TABLES
-- =============================================================================

CREATE TABLE IF NOT EXISTS evidence_records (
    id SERIAL PRIMARY KEY,
    evidence_type VARCHAR(30) NOT NULL,           -- SOURCE, LLM_EXTRACTION, ENTITY_RESOLUTION, RISK_CALCULATION, SCENARIO_COMPUTATION, OPTIMIZATION, RECOMMENDATION
    source_url TEXT,                              -- Original source URL (for SOURCE type)
    source_name VARCHAR(100),                    -- Data source identifier
    timestamp TIMESTAMP DEFAULT NOW(),           -- When this evidence was created
    related_entity_type VARCHAR(30),             -- event, risk_score, scenario_result, procurement_option
    related_entity_id INT,                       -- FK to the related entity
    model_or_method VARCHAR(100),                -- LLM model name, algorithm version, formula ID
    input_summary JSONB,                         -- Summary of inputs used
    output_summary JSONB,                        -- Summary of outputs produced
    data_semantic VARCHAR(30),                   -- OBSERVED, DERIVED, HISTORICAL_CALIBRATED, ASSUMED, SIMULATED
    confidence DECIMAL(5,3),                     -- 0.0–1.0
    notes TEXT                                   -- Human-readable context
);

CREATE TABLE IF NOT EXISTS evidence_links (
    id SERIAL PRIMARY KEY,
    parent_evidence_id INT REFERENCES evidence_records(id) NOT NULL,  -- Upstream evidence
    child_evidence_id INT REFERENCES evidence_records(id) NOT NULL,   -- Downstream evidence
    relationship VARCHAR(30)                     -- DERIVED_FROM, CONTRIBUTED_TO, USED_IN
);

-- =============================================================================
-- DATA SOURCE TRACKING
-- =============================================================================

CREATE TABLE IF NOT EXISTS data_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,                  -- GDELT, ACLED, EIA, etc.
    url TEXT,
    update_frequency VARCHAR(50),
    last_fetched_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ACTIVE',         -- ACTIVE, STALE, ERROR, UNAVAILABLE
    classification VARCHAR(20)                   -- OBSERVED, HISTORICAL_CALIBRATED
);

-- =============================================================================
-- ENTITY RESOLUTION SUPPORT
-- =============================================================================

CREATE TABLE IF NOT EXISTS entity_aliases (
    id SERIAL PRIMARY KEY,
    alias VARCHAR(200) NOT NULL,                 -- The variant string (e.g., "Saudi Aramco", "Hormuz")
    canonical_entity_type VARCHAR(30) NOT NULL,   -- country, corridor, supplier, port, refinery, crude_grade
    canonical_entity_id INT NOT NULL,             -- FK to the corresponding reference table
    match_type VARCHAR(20),                       -- EXACT, FUZZY, ALIAS
    created_at TIMESTAMP DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_events_detected_at ON geopolitical_events(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_events_type ON geopolitical_events(event_type);
CREATE INDEX IF NOT EXISTS idx_risk_scores_entity ON risk_scores(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_risk_scores_calculated ON risk_scores(calculated_at DESC);
CREATE INDEX IF NOT EXISTS idx_commodity_prices_source_ts ON commodity_prices(source_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_fx_rates_source_ts ON fx_rates(source_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_evidence_related ON evidence_records(related_entity_type, related_entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_aliases_lookup ON entity_aliases(canonical_entity_type, canonical_entity_id);
