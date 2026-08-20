-- =============================================================================
-- INDRA — Seed Data (PostgreSQL)
-- =============================================================================
-- STATUS: PLACEHOLDER — Seed data will be populated during implementation.
--
-- This file will contain INSERT statements for India-specific reference data:
--   - Countries (supplier nations + India)
--   - Suppliers (~8 major crude suppliers to India)
--   - Refineries (~20 Indian refineries with capacity and crude compatibility)
--   - Ports (~10 major Indian crude-receiving ports + origin ports)
--   - Routes (~15+ supply routes with chokepoint flags)
--   - Strategic Reserves (3 ISPRL locations)
--   - Crude Grades (major grades imported by India)
--   - Data Sources (registry of all external data feeds)
--   - Preset Scenarios (4-5 preset disruption scenarios)
--
-- All seed data must come from verified public sources:
--   - PPAC Annual Report 2024-25
--   - ISPRL official website
--   - Company annual reports (IOC, BPCL, HPCL, Reliance, MRPL)
--   - MoPNG publications
--
-- Do NOT fabricate refinery throughput numbers, crude import volumes,
-- or SPR fill levels without citing a public source.
-- =============================================================================

-- Placeholder: Countries will be seeded here
-- INSERT INTO countries (name, iso3, base_risk_score, region, is_hormuz_dependent, is_red_sea_dependent) VALUES ...

-- Placeholder: Suppliers will be seeded here
-- INSERT INTO suppliers (name, country_id, crude_grades, annual_supply_capacity_mmtpa, ...) VALUES ...

-- Placeholder: Ports will be seeded here
-- INSERT INTO ports (name, un_locode, country_id, is_indian, latitude, longitude, ...) VALUES ...

-- Placeholder: Refineries will be seeded here (source: PPAC Annual Report)
-- INSERT INTO refineries (name, owner, state, capacity_mmtpa, compatible_crude_grades, ...) VALUES ...

-- Placeholder: Routes will be seeded here
-- INSERT INTO routes (name, origin_port_id, dest_port_id, distance_nm, avg_transit_days, ...) VALUES ...

-- Placeholder: Strategic Reserves (source: ISPRL official data)
-- INSERT INTO strategic_reserves (location_name, operator, state, capacity_mmt, ...) VALUES
--   ('Visakhapatnam', 'ISPRL', 'Andhra Pradesh', 1.33, ...),
--   ('Mangalore', 'ISPRL', 'Karnataka', 1.50, ...),
--   ('Padur', 'ISPRL', 'Karnataka', 2.50, ...);

-- Placeholder: Data Sources registry
-- INSERT INTO data_sources (name, url, update_frequency, classification) VALUES
--   ('GDELT', 'gdeltproject.org', '15 minutes', 'LIVE'),
--   ('ACLED', 'acleddata.com', 'Weekly', 'RECENT'),
--   ('EIA', 'api.eia.gov', 'Daily', 'RECENT'),
--   ('RBI', 'rbi.org.in', 'Daily', 'RECENT'),
--   ('OFAC', 'sanctionslist.treasury.gov', 'Daily', 'LIVE'),
--   ('PPAC', 'ppac.gov.in', 'Monthly', 'HISTORICAL'),
--   ('ISPRL', 'isprl.gov.in', 'Annual', 'HISTORICAL');

-- Placeholder: Preset Scenarios
-- INSERT INTO scenarios (name, scenario_type, parameters) VALUES
--   ('Hormuz Full Closure', 'HORMUZ_FULL', '{"capacity_reduction_pct": 100, ...}'),
--   ('Hormuz 50% Disruption', 'HORMUZ_PARTIAL', '{"capacity_reduction_pct": 50, ...}'),
--   ('Russia Supply Loss', 'RUSSIA_LOSS', '{"volume_loss_pct": 100, ...}'),
--   ('Red Sea Suspension', 'RED_SEA', '{"capacity_reduction_pct": 100, ...}');
