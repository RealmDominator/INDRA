# INDRA — Scenario Engine

> Source: PETRAS Analysis §13; INDRA Master Report §15
>
> The scenario engine is deterministic and parametric. No LLM or ML model is involved in scenario computation.
>
> **Revision:** Post-review corrections. Added data semantic classification, provenance tracking, refinery_supply_mix reference. NetworkX graph traversal role explicitly defined.

---

## Purpose

The scenario engine models "what-if" disruption scenarios by propagating a controlled perturbation through India's supply-chain graph and calculating the downstream impact.

A scenario is a set of assumptions about a disruption event, applied to the current state of the supply network.

---

## Scenario Inputs

| Parameter | Type | Description |
|---|---|---|
| `scenario_type` | Enum | HORMUZ_FULL, HORMUZ_PARTIAL, RUSSIA_LOSS, RED_SEA, PRICE_SPIKE |
| `capacity_reduction_pct` | 0–100 | Percentage of corridor/supplier capacity lost |
| `duration_days` | 1–365 | Duration of the disruption |
| `affected_countries` | List | Countries whose supply is affected |
| `freight_multiplier` | Float | Multiplier on freight cost for alternate routes |
| `price_impact_per_barrel` | Float (USD) | Estimated per-barrel price increase |

---

## Preset Scenarios

### 1. Hormuz Full Closure (100%)

```
capacity_reduction_pct: 100
default_duration_days: 30
affected_countries: [Iraq, Iran, Kuwait, Saudi Arabia, UAE, Qatar, Bahrain]
alternate_routes: [Cape of Good Hope]
freight_multiplier: 3.2    (Cape route is ~3x longer than Hormuz route)
insurance_premium_increase_pct: 400
price_impact_per_barrel: $15.0    (calibration source: Gulf War II, EIA historical)
```

### 2. Hormuz Partial Disruption (50%)

```
capacity_reduction_pct: 50
freight_multiplier: 1.4
price_impact_per_barrel: $5.0
```

### 3. Russia Supply Loss

```
affected_supplier: Russia
volume_loss_pct: 100    (India loses ~36-38% of crude supply)
alternate_suppliers: [Saudi Arabia, Iraq, USA, Nigeria]
price_impact_per_barrel: $10.0
reachable_in_days: 30
```

### 4. Red Sea Full Suspension

```
capacity_reduction_pct: 100
alternate_routes: [Cape of Good Hope]
freight_multiplier: 2.8
price_impact_per_barrel: $3.0
```

### 5. (Optional) Crude Price Spike +15%

```
brent_increase_pct: 15
forex_pressure_estimate: moderate
```

---

## Disruption Assumptions

> **Important:** The following are modeled assumptions based on historical precedent and public data. They are NOT real-time measurements. All scenario outputs must be labeled as "estimated" or "derived."

### Key Constants

| Constant | Value | Source |
|---|---|---|
| India daily crude import | ~0.56 MMT/day | Derived from PPAC annual import data (~205 MMT/year) |
| Hormuz-dependent share | ~42% | PPAC import-by-source data |
| Russia share | ~36–38% | PPAC FY2025 approximate |
| Total SPR capacity | 5.33 MMT | ISPRL official data |
| Days of SPR coverage | ~9.5 days | Derived: 5.33 / 0.56 |
| Brent-to-barrel conversion | 7.33 barrels per MT | Standard industry conversion |

### Calibration Sources

Scenario multipliers should be calibrated against historical disruption data:

| Historical Event | EIA Data Available | Relevant For |
|---|---|---|
| Gulf War II (2003) | ✅ | Hormuz/Middle East disruption magnitude |
| Libya disruption (2011) | ✅ | Supply loss impact on prices |
| Houthi Red Sea attacks (2023-24) | ✅ | Red Sea disruption, freight impact |
| Russia-Ukraine (2022-) | ✅ | Russia supply rerouting, discount structure |
| COVID demand crash (2020) | ✅ | Price spike/crash calibration |

> **Critical:** Show calibration data to judges. This is the difference between a credible model and a "random numbers generator."
>
> All calibration values carry data_semantic = **HISTORICAL_CALIBRATED**.

---

## Propagation Logic

```
1. DISRUPTION APPLIED
   [Arithmetic] Mark corridor/supplier as disrupted at specified severity

2. AFFECTED SUPPLIER FLOWS
   [NetworkX] Traverse graph: identify all suppliers whose routes pass through
              the disrupted corridor (supplier → route → corridor traversal)
   [Arithmetic] Calculate volume loss per supplier:
              supplier_volume × (capacity_reduction_pct / 100)

3. ROUTE CAPACITY REDUCED
   [NetworkX] Traverse graph: find all routes passing through the disrupted
              corridor; mark those routes as capacity-reduced
   [NetworkX] Find alternative paths: identify feasible routes from affected
              suppliers to destination ports that avoid the disrupted corridor
   [Arithmetic] For each affected route:
              available_capacity *= (1 - capacity_reduction_pct / 100)

4. REFINERY INTAKE REDUCED
   [NetworkX] Traverse graph: identify all refineries downstream of disrupted
              routes (port → refinery edges)
   [PostgreSQL] Look up crude grade dependencies via refinery_supply_mix table
   [Arithmetic] Calculate feedstock shortfall based on compatibility and share
   [NetworkX] Check reachability: do compatible alternative crude grades
              exist via non-disrupted routes?

5. INVENTORY BURN ESTIMATED
   [Arithmetic] For affected refineries:
              days_to_minimum = current_inventory / (normal_intake - disrupted_intake)

6. NATIONAL SUPPLY GAP
   [Arithmetic] total_gap = Σ(refinery_shortfalls)

7. SPR BRIDGE REQUIREMENT
   [Arithmetic] required_spr = gap that cannot be covered by alternative procurement
              days_bridged = available_spr / daily_gap
              remaining_reserve = total_spr - drawdown

8. COST IMPACT
   [Arithmetic] additional_cost = price_impact × volume × duration_factor
              freight_cost = (disrupted_freight - normal_freight) × affected_volume
```

---

## NetworkX / PostgreSQL / Arithmetic Boundary

The scenario engine operates in three distinct layers. Each is responsible for a different type of work:

| Layer | Component | What it does in the scenario pipeline |
|---|---|---|
| **Graph traversal** | NetworkX (in-memory) | Answers *which entities are affected*: which refineries downstream, which routes disrupted, which alternative paths exist |
| **Persistent data** | PostgreSQL | Source of truth for all entity attributes: capacities, shares, compatibility, SPR levels, corridor risk scores |
| **Arithmetic calculation** | Scenario Engine (Python) | Computes *how much impact*: supply gap, volume loss, days-to-critical, cost impact, SPR bridge requirement |

> **The scenario engine does not traverse the supply graph itself.** It calls the NetworkX layer to get the list of affected refineries and feasible alternative routes, then applies the documented arithmetic formulas to those results.

---

## Supply Impact Calculation

```python
# Conceptual — not implemented
def calculate_supply_impact(scenario, current_state):
    india_daily_import_mmt = 0.56
    
    if scenario.type.startswith("HORMUZ"):
        hormuz_share = 0.42
        affected_volume_per_day = (
            india_daily_import_mmt
            * hormuz_share
            * (scenario.capacity_reduction_pct / 100)
        )
    elif scenario.type == "RUSSIA_LOSS":
        russia_share = 0.37
        affected_volume_per_day = (
            india_daily_import_mmt
            * russia_share
            * (scenario.volume_loss_pct / 100)
        )
    
    total_supply_gap = affected_volume_per_day * scenario.duration_days
    days_until_critical = current_state.spr_level_mmt / affected_volume_per_day
    
    return {
        "supply_gap_mmt": total_supply_gap,
        "affected_volume_per_day_mmt": affected_volume_per_day,
        "days_until_critical": days_until_critical,
    }
```

---

## Refinery Impact Calculation

For each affected refinery:
1. Determine which supplier routes are disrupted
2. Calculate the feedstock shortfall based on the refinery's supplier mix
3. Check if compatible alternative crude grades exist via non-disrupted routes
4. Calculate days to minimum stock based on current throughput and shortfall

---

## SPR Impact Calculation

```
Inputs:
  scenario_supply_gap_mmt
  spr_available_mmt (from strategic_reserves table)
  max_drawdown_rate_mmt_per_day (physical limitation of SPR facilities)
  required_bridge_duration_days

Outputs:
  recommended_drawdown_mmt = min(scenario_supply_gap_mmt, spr_available_mmt)
  remaining_reserve_mmt = spr_available_mmt - recommended_drawdown_mmt
  days_bridged = recommended_drawdown_mmt / daily_gap_mmt
  uncovered_gap_mmt = max(0, scenario_supply_gap_mmt - spr_available_mmt)
```

> **Wording:** Use "Modelled SPR support requirement" — NOT "Government-approved drawdown recommendation."

---

## Output Format

```json
{
  "scenario_id": 7,
  "scenario_type": "HORMUZ_PARTIAL",
  "parameters": {
    "capacity_reduction_pct": 50,
    "duration_days": 30
  },
  "results": {
    "supply_gap_mmt": 7.06,
    "days_until_critical": 22.7,
    "price_impact_per_barrel_usd": 5.0,
    "additional_import_cost_usd_bn": 1.9,
    "additional_freight_cost_usd_bn": 0.8,
    "affected_refineries": ["BPCL Kochi", "IOC Paradip", "MRPL Mangalore"],
    "alternative_routes": ["Cape of Good Hope"],
    "spr_bridge": {
      "required_mmt": 3.2,
      "available_mmt": 5.33,
      "days_bridged": 5.7,
      "uncovered_gap_mmt": 0
    }
  },
  "assumptions": [
    {"name": "india_daily_import_mmt", "value": 0.56, "data_semantic": "HISTORICAL_CALIBRATED", "source": "PPAC annual import data"},
    {"name": "hormuz_share", "value": 0.42, "data_semantic": "HISTORICAL_CALIBRATED", "source": "PPAC import-by-source FY2024-25"},
    {"name": "price_impact_per_barrel", "value": 5.0, "data_semantic": "HISTORICAL_CALIBRATED", "source": "EIA Gulf War II / Houthi data"},
    {"name": "freight_multiplier", "value": 1.4, "data_semantic": "ASSUMED", "source": "Cape/Hormuz distance ratio estimate"},
    {"name": "spr_total_capacity", "value": 5.33, "data_semantic": "OBSERVED", "source": "ISPRL official data"}
  ],
  "data_semantic": "DERIVED"
}
```

> **REMOVED from MVP:** `gdp_impact_estimate` — GDP impact estimation requires macroeconomic modeling beyond this system's scope.

---

## Data Semantic Classification for Scenario Values

| Element | Data Semantic | Label | Source |
|---|---|---|---|
| India daily import rate | HISTORICAL_CALIBRATED | Derived from PPAC data | PPAC annual report |
| Hormuz share percentage | HISTORICAL_CALIBRATED | Derived from PPAC source data | PPAC FY2024-25 |
| Russia share percentage | HISTORICAL_CALIBRATED | Derived from PPAC source data | PPAC FY2024-25 |
| Freight multiplier (3.2x for Cape) | ASSUMED | Configuration assumption | Distance ratio estimate |
| Price impact ($15/bbl) | HISTORICAL_CALIBRATED | Calibrated from historical data | EIA Gulf War II data |
| SPR capacity | OBSERVED | ISPRL official data | ISPRL website |
| Supply gap formula | DERIVED | Deterministic calculation | Documented formula |
| Days-to-critical formula | DERIVED | Deterministic calculation | Documented formula |
| Refinery exposure | DERIVED | Calculated from refinery_supply_mix | refinery_supply_mix table |

Every scenario output must make this distinction clear in the evidence panel.

---

## Provenance

Every scenario computation creates an `evidence_records` entry:
```json
{
  "evidence_type": "SCENARIO_COMPUTATION",
  "model_or_method": "parametric_scenario_v1",
  "input_summary": {"scenario_type": "HORMUZ_PARTIAL", "capacity_reduction_pct": 50, "duration_days": 30},
  "output_summary": {"supply_gap_mmt": 7.06, "days_until_critical": 22.7},
  "data_semantic": "DERIVED"
}
```

The evidence record links back to the risk scores and events that triggered the scenario.
