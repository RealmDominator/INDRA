# INDRA — Procurement Optimization Engine

> Source: PETRAS Analysis §14; INDRA Master Report §16
>
> The procurement engine is algorithmic — not LLM-generated. Phase 1 uses deterministic linear programming with deterministic ranking fallback.
>
> **Revision:** Post-review corrections. References crude_grades and refinery_supply_mix tables. Added provenance tracking.

> **Step 8D-A status:** COMPLETE. The implementation uses `scipy.optimize.linprog(method="highs")` when supplier, crude-grade, route, capacity, cost, risk, compatibility, and route-status inputs are known. Incomplete legacy payloads, unavailable SciPy, and solver failures use the existing deterministic ranking fallback. Step 8D-B is NOT STARTED.

---

## Optimization Objective

Find the minimum-cost, minimum-risk procurement mix that satisfies refinery crude requirements while respecting sanctions, compatibility, and capacity constraints.

### Formal Objective

```
Minimize: Σ (price_cif[i,j] + risk_penalty[i,j]) × volume[i,j]

WHERE:
  i = supplier (Russia, Saudi Arabia, Iraq, USA, Nigeria, ...)
  j = route (Hormuz, Cape, Direct, Atlantic, ...)
```

### Risk Penalty

```
risk_penalty[i,j] = λ × route_risk[i,j] × price_cif[i,j]
```

Where `λ` is a risk aversion parameter that can be adjusted by the user (higher λ = more risk-averse procurement).

---

## Constraints

| # | Constraint | Formulation |
|---|---|---|
| 1 | **Volume requirement** | `Σ volume[i,j] >= target_volume` — meet the supply gap |
| 2 | **Supplier capacity** | `volume[i,j] <= available_capacity[i,j]` — can't exceed what supplier can deliver |
| 3 | **Sanctions compliance** | `volume[i,j] = 0 if is_sanctioned[i] = True` — OFAC/EU/UN compliance |
| 4 | **Route operational** | `volume[i,j] = 0 if is_route_disrupted[j] = True` — can't use disrupted routes |
| 5 | **Crude compatibility** | `refinery_supply_mix.compatibility_score >= threshold` — refinery must accept grade |

**Compatibility threshold (frozen):** Default **0.5** — grades with MEDIUM or higher compatibility are included. Grades below 0.5 or `compatibility = NONE` are excluded. Configurable in `config/optimization.yaml`.
| 6 | **Risk tolerance** | `risk_score[i,j] <= max_risk_tolerance` — optional risk ceiling |
| 7 | **Concentration limit** | `Σ volume[russia,j] <= russia_cap` — diversification constraint |
| 8 | **Transit time** | `transit_days[j] <= max_acceptable_transit` — operational deadline |

---

## Input Data

### Suppliers

| Field | Description |
|---|---|
| supplier_id | Identifier |
| name | Supplier name |
| country | Origin country |
| crude_grades | Available crude grades |
| annual_capacity_mmtpa | Maximum supply capacity |
| is_sanctioned | OFAC/sanctions status |
| current_risk_score | Supplier-level risk |

### Routes

| Field | Description |
|---|---|
| route_id | Identifier |
| origin_port | Departure port |
| dest_port | Indian receiving port |
| distance_nm | Nautical miles |
| transit_days | Average transit time |
| chokepoints | Which chokepoints are traversed |
| is_operational | Is route currently usable? |
| risk_score | Current route risk |
| freight_rate_per_mt | Estimated freight cost |

### Prices

| Field | Description |
|---|---|
| crude_grade | Grade name |
| price_fob_usd | Free-on-board price per barrel |
| freight_usd_per_mt | Route-specific freight |
| insurance_premium | War-risk / standard insurance |
| price_cif_usd | CIF = FOB + freight + insurance |

### Compatibility

Compatibility data comes from the `refinery_supply_mix` table, which references the `crude_grades` table:

| Refinery | Crude Grade (via crude_grades.name) | Compatibility | Score |
|---|---|---|---|
| BPCL Kochi | Basrah Light | HIGH | 0.9 |
| BPCL Kochi | Bonny Light | HIGH | 0.85 |
| BPCL Kochi | Arab Light | MEDIUM | 0.7 |
| BPCL Kochi | WTI | MEDIUM | 0.65 |
| IOC Panipat | Arab Light | HIGH | 0.9 |
| IOC Panipat | Urals | MEDIUM | 0.7 |

> **Note:** Compatibility values are looked up from `refinery_supply_mix.compatibility_score`. Values marked with `source_type = 'ESTIMATED'` in the mix table are prototype domain assumptions. Do not present synthetic refinery-intake numbers as official refinery engineering limits.
>
> **Crude grade matching:** Supplier grades and refinery compatibility both reference the `crude_grades` reference table, ensuring consistent naming. No free-form text matching.

---

## Implementation Approach

### Primary: SciPy Linear Programming (Phase 1)

For each eligible supplier–crude-grade–route candidate, the optimizer chooses a continuous allocation `x_k` in MMT and minimizes effective landed cost:

```
effective_unit_cost[k]
  = unit_cost[k] × (1 + risk_aversion × risk_score[k])
    + transit_penalty_per_day × transit_days[k]

Minimize: Σ effective_unit_cost[k] × x_k
```

The current implementation calls `scipy.optimize.linprog` with the HiGHS method. Allocations are deterministic for the same validated candidate set and parameters.

### Fallback: Deterministic Ranking

For each candidate supplier-route-grade combination:

```
score = w1 × compatibility
      + w2 × (1 - normalized_cost)
      + w3 × (1 - normalized_risk)
      + w4 × (1 - normalized_transit_time)
      + w5 × (1 if compliant else 0)
      + w6 × diversification_bonus
```

Filter out:
1. Incompatible grades (`compatibility_score < 0.5` or `compatibility = NONE`)
2. Sanctioned suppliers
3. Disrupted routes (per active scenario)

Sort by score, return top 3–5 options.

The fallback preserves the existing stable ranking behavior for legacy candidates that do not identify a supplier, crude grade, and route, or when required numerical inputs are unknown. It never substitutes fabricated capacity, cost, compatibility, or transit values.

### LP Constraints and Eligibility

The implementation applies these rules before solving:

| Constraint | Implementation behavior |
|---|---|
| Required supply volume | Equality constraint `Σ x_k = target_volume`; target is normally the scenario supply gap. |
| Supplier availability | Upper bound `x_k ≤ available_volume`; unknown capacity is excluded from LP. |
| Route capacity | If known, upper bound is additionally limited by `route_capacity`. |
| Route availability | `is_operational=False` or `route_operational=False` excludes the candidate. |
| Route disruption | `is_route_disrupted=True` or `route_disrupted=True` excludes the candidate. |
| Sanctions | `is_sanctioned=True` excludes the candidate. |
| Crude compatibility | Missing compatibility is unknown and excluded; scores below the default 0.5 threshold are excluded. |
| Transit time | If `max_transit_days` is supplied, missing or excessive transit time excludes the candidate. Otherwise known transit time contributes the configured penalty. |
| Infeasibility | Solver status is `INFEASIBLE`; the result remains `feasible=false` and includes the deterministic fallback allocation and reason. |

The LP requires `supplier_id`, `crude_grade_id`, and `route_id`. This prevents ambiguous allocations and ensures the result can identify all three domain entities.

---

## Output Format

### Step 8D-A Result Contract

`optimize_procurement` returns:

- `selected`: supplier, crude grade, route, allocated volume, unit cost, risk, transit, and compatibility;
- `objective_value`: effective objective value for an optimal LP result, otherwise `null` when fallback values are not safely computable;
- `solver_status`: `OPTIMAL`, `INFEASIBLE`, or `FALLBACK`;
- `constraints`: target, threshold, transit/risk parameters, exclusions, and route/sanctions rules;
- `fallback_used` and `fallback_reason`;
- `data_semantic: DERIVED`;
- `provenance` and `evidence` optimization-stage records containing method and input constraint metadata.

### Ranked Recommendations

```json
{
  "refinery": "BPCL Kochi",
  "supply_gap_mmt": 1.2,
  "alternatives": [
    {
      "rank": 1,
      "supplier": "Saudi Arabia",
      "crude_grade": "Arab Light",
      "compatibility": "HIGH",
      "route": "Cape of Good Hope",
      "transit_days": 21,
      "price_fob_usd_per_barrel": 82.50,
      "freight_usd_per_barrel": 3.50,
      "price_cif_usd_per_barrel": 86.00,
      "cost_premium_vs_normal": "+$3.50/bbl",
      "route_risk_score": 0.15,
      "sanctions_status": "CLEAR",
      "overall_score": 0.87,
      "volume_available_mmt": 2.5
    },
    {
      "rank": 2,
      "supplier": "Nigeria",
      "crude_grade": "Bonny Light",
      "compatibility": "HIGH",
      "route": "Atlantic Direct",
      "transit_days": 18,
      "price_cif_usd_per_barrel": 88.30,
      "cost_premium_vs_normal": "+$5.80/bbl",
      "route_risk_score": 0.10,
      "sanctions_status": "CLEAR",
      "overall_score": 0.82,
      "volume_available_mmt": 0.8
    }
  ]
}
```

---

## Explainability Requirements

Every procurement recommendation must be explainable:

1. **Why this supplier?** — Compatibility score, available volume, compliance status
2. **Why this route?** — Risk score, transit time, freight cost vs alternatives
3. **Why this ranking?** — Show all scoring components and weights
4. **What changes it?** — If the scenario parameters change, the recommendation must change demonstrably

> **Critical test:** Change one scenario parameter and verify the recommendation changes. If the output is static regardless of input, the optimizer is fake.

---

## Risk Aversion Parameter (λ)

The user should be able to adjust risk tolerance:

| λ Value | Behavior |
|---|---|
| 0.0 | Pure cost minimization (ignore risk) |
| 0.5 | Balanced cost + risk |
| 1.0 | Strong risk aversion (willing to pay premium for safety) |
| 2.0+ | Extreme risk aversion |

This parameter should be adjustable in the UI and visibly changes the procurement ranking.

---

## Provenance

Every procurement optimization run creates an `evidence_records` entry:
```json
{
  "evidence_type": "OPTIMIZATION",
  "model_or_method": "deterministic_ranking_v1",
  "input_summary": {"scenario_id": 7, "refinery": "BPCL Kochi", "supply_gap_mmt": 1.2, "risk_aversion": 0.5},
  "output_summary": {"top_alternative": "Arab Light via Cape", "ranking_score": 0.87},
  "data_semantic": "DERIVED"
}
```

The evidence record links back to the scenario result that triggered the optimization.
