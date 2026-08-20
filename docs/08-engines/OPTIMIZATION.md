# INDRA — Procurement Optimization Engine

> Source: PETRAS Analysis §14; INDRA Master Report §16
>
> The procurement engine is algorithmic — not LLM-generated. It uses deterministic ranking or linear programming.

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
| 5 | **Crude compatibility** | Refinery must be compatible with the crude grade offered | 
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

| Refinery | Crude Grade | Compatibility Score |
|---|---|---|
| BPCL Kochi | Basrah Light | HIGH (0.9) |
| BPCL Kochi | Bonny Light | HIGH (0.85) |
| BPCL Kochi | Arab Light | MEDIUM (0.7) |
| BPCL Kochi | WTI | MEDIUM (0.65) |
| IOC Panipat | Arab Light | HIGH (0.9) |
| IOC Panipat | Urals | MEDIUM (0.7) |

> **Note:** Compatibility values are prototype domain assumptions unless backed by verified public/company data. Do not present synthetic refinery-intake numbers as official refinery engineering limits.

---

## Implementation Approach

### Primary: Deterministic Ranking (Simpler, Reliable)

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
1. Incompatible grades (compatibility = NONE)
2. Sanctioned suppliers
3. Disrupted routes (per active scenario)

Sort by score, return top 3–5 options.

### Secondary: LP Optimization (scipy/PuLP)

If the deterministic ranking is implemented and stable, upgrade to a proper LP formulation:

```python
# Conceptual — not implemented
from scipy.optimize import linprog

def optimize_procurement(suppliers, routes, target_volume,
                         disrupted_routes, sanctioned_suppliers,
                         risk_tolerance=0.5):
    n = len(suppliers) * len(routes)
    
    # Objective: minimize cost + risk penalty
    c = []
    for s in suppliers:
        for r in routes:
            if s.is_sanctioned or r.id in disrupted_routes:
                c.append(1e9)  # effectively exclude
            else:
                cost = s.price_cif + risk_tolerance * s.risk * r.risk * s.price_cif
                c.append(cost)
    
    # Constraint: total volume = target
    A_eq = [[1] * n]
    b_eq = [target_volume]
    
    # Bounds: capacity limits
    bounds = [(0, s.capacity * r.availability) 
              for s in suppliers for r in routes]
    
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    return parse_result(result, suppliers, routes)
```

This is real optimization. Judges who are technically strong will recognize it.

---

## Output Format

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
