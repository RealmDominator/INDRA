# INDRA — UI/UX Specification

> Source: PETRAS Analysis §16, §21; INDRA Master Report §10, §21

---

## Target User Profile

| Attribute | Detail |
|---|---|
| Role | Crude procurement analyst, refinery supply-chain manager, government policy adviser |
| Technical level | Domain expert, not a software engineer |
| Decision context | Time-pressured during crisis; deliberative during planning |
| Current tools | Bloomberg terminal, Reuters Eikon, Excel models, internal reports |
| What they need | Actionable intelligence, not raw data; explainable recommendations, not black boxes |

## Design Principles

1. **Information density over decoration** — These are professional decision-makers. Prioritize data clarity over aesthetic flourishes.
2. **Evidence-first** — Every score, recommendation, and calculation must be inspectable. No unexplained numbers.
3. **Data classification visible** — Every data element must show whether it is LIVE, RECENT, HISTORICAL, DERIVED, or SIMULATED.
4. **Crisis-appropriate** — Risk levels must be immediately scannable. Red = urgent. Green = normal.
5. **Progressive disclosure** — Summary → detail → evidence → source. Don't overwhelm the first view.

---

## Primary User Workflow

```
1. User opens INDRA → sees Risk Overview dashboard
2. Scans corridor risk cards (Hormuz, Red Sea, Russia, etc.)
3. Notices elevated risk on Hormuz → clicks WHY?
4. Evidence panel shows: source articles + extracted events + risk components
5. Opens Scenario Simulator
6. Selects: Hormuz = 50% disruption, Duration = 30 days
7. INDRA calculates and displays:
   - Refinery-level supply gap
   - Days-to-minimum-stock
   - National shortfall
   - SPR bridge requirement
8. User selects a specific refinery
9. INDRA ranks compatible procurement alternatives
10. User inspects evidence for top recommendation
11. LLM-generated action brief summarizes findings
12. User can export or share the analysis
```

---

## Page Structure

### Page 1: Risk Overview (Landing Page)

**Purpose:** Immediate situational awareness.

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  INDRA — India Energy Disruption Monitor                    │
│  Data Status: LIVE / RECENT / ESTIMATED                     │
│  Last Updated: [timestamp]                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ HORMUZ   │ │ RED SEA  │ │ RUSSIA   │ │ SUEZ     │      │
│  │ Score:78 │ │ Score:61 │ │ Score:48 │ │ Score:31 │      │
│  │ CRITICAL │ │ HIGH     │ │ MODERATE │ │ MODERATE │      │
│  │ ▲ +12    │ │ ▲ +5     │ │ ─ 0     │ │ ▼ -3    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Recent Events                                          │ │
│  │ • [2 min ago] MILITARY: IRGC naval drills near Hormuz │ │
│  │ • [1 hr ago] SANCTION: US sanctions 3 Iranian tankers │ │
│  │ • [6 hr ago] DIPLOMATIC: Iran nuclear talks stall     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Quick Stats                                            │ │
│  │ India Daily Import: 0.56 MMT │ Hormuz Share: 42%      │ │
│  │ SPR: 5.33 MMT (9.5 days)    │ Brent: $XX.XX          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Risk Card Contents:**
- Risk score (0–100)
- Risk level label (LOW / MODERATE / HIGH / CRITICAL / EXTREME)
- Trend indicator (arrow up/down/neutral + delta from last period)
- Top contributing events (count)
- Last update timestamp
- Confidence / data quality indicator

### Page 2: India Supply Network Map

**Purpose:** Geographic visualization of India's energy supply network.

**Map Elements:**
- **Refineries** — Markers with capacity tooltip (~20 Indian refineries)
- **Ports** — Markers with throughput data
- **SPR locations** — Distinct markers (3 locations: Visakhapatnam, Mangalore, Padur)
- **Chokepoints** — Highlighted zones (Hormuz, Bab el-Mandeb, Suez, Malacca)
- **Supply routes** — Lines colored by current risk (green→yellow→red gradient)
- **Supplier countries** — Origin markers

**Map Interactions:**
- Click route → show risk score + evidence
- Click refinery → show capacity, compatible crude grades, current risk exposure
- Click SPR → show capacity, current level, days coverage
- Toggle scenario overlay (before/after disruption)

**Important:** No fake "live tanker" positions. If vessel positions are shown, they must be clearly labeled as "Historical route baseline" or "Scenario simulation."

### Page 3: Scenario Simulator

**Purpose:** Interactive disruption scenario modeling.

**Inputs:**
- Scenario type selector (dropdown: Hormuz 50%, Hormuz 100%, Russia supply loss, Red Sea disruption)
- Duration slider (days)
- Optional: severity percentage slider

**Outputs:**
```
┌────────────────────────────────────────────┐
│ Scenario Results                            │
│                                            │
│ National Supply Gap:     X.XX MMT          │
│ Most Exposed Refineries: [list]            │
│ Days to Minimum Stock:   X.X days          │
│ SPR Bridge Requirement:  X.XX MMT          │
│ Est. Additional Cost:    $X.X billion      │
│ Freight Impact:          +XXX%             │
│ Alternative Routes:      [list]            │
│                                            │
│ ⚠ All values are ESTIMATED / DERIVED      │
│ Based on: [scenario parameters listed]     │
└────────────────────────────────────────────┘
```

**Important:** All scenario outputs must be marked as "estimated" or "derived." They must never be presented as measured real-time inventory or confirmed figures.

### Page 4: Procurement Recommendations

**Purpose:** Ranked alternative crude procurement options for a selected refinery.

**Inputs:**
- Refinery selector (dropdown)
- Active scenario context (from Page 3)

**Output Table:**
```
Rank | Crude Grade  | Origin      | Compatibility | Route      | Transit | Cost Premium | Risk  | Compliance | Score
1    | Arab Light   | Saudi Arabia| High          | Cape       | 21 days | +$3.50/bbl   | Low   | Clear      | 0.87
2    | Bonny Light  | Nigeria     | High          | Atlantic   | 18 days | +$2.80/bbl   | Low   | Clear      | 0.82
3    | Urals        | Russia      | Medium        | Cape       | 25 days | +$4.20/bbl   | Medium| ⚠ Shadow   | 0.64
```

**Evidence link:** Each row links to detailed scoring breakdown.

### Page 5 (Drawer/Panel): Evidence Trail

**Purpose:** Full drill-down from any displayed score or recommendation to its source chain.

**Example Evidence Display:**
```
ROUTE RISK: Hormuz — Score: 78 (CRITICAL)  [Last updated: 10 min ago]

WHY?
├── Geopolitical Component: 82/100 (weight: 25%)
│   ├── [2026-08-19] "IRGC naval drills near Hormuz"
│   │   severity: 0.7 | Source: Reuters via GDELT
│   │   Classified by: LLM | Verified: No | Confidence: 0.75
│   ├── [2026-08-17] "US sanctions on 3 Iranian tankers"
│   │   severity: 0.6 | Source: OFAC
│   │   Verified: Yes | Confidence: 1.0
│   └── Base country risk (Iran): 0.85
│
├── Chokepoint Exposure: 90/100 (weight: 20%)
│   └── Hormuz handles ~42% of India crude imports
│
├── Historical Rate: 45/100 (weight: 10%)
│   └── 3 disruptions in last 5 years
│
└── India Dependency: 42/100 (weight: 10%)
    └── 42% of imports transit this corridor

CONFIDENCE: 0.72
DATA FRESHNESS:
  Geopolitical: 10 min ago (LIVE)
  Prices: today (RECENT)
  Import structure: PPAC FY2024-25 (HISTORICAL)
```

---

## SPR Information Display

```
┌────────────────────────────────────────────┐
│ Strategic Petroleum Reserves               │
│                                            │
│ Location        Capacity  Level   Coverage │
│ Visakhapatnam   1.33 MMT  X MMT   X days  │
│ Mangalore       1.50 MMT  X MMT   X days  │
│ Padur           2.50 MMT  X MMT   X days  │
│ ─────────────────────────────────────────  │
│ Total           5.33 MMT  X MMT   ~9.5 d  │
│                                            │
│ Under scenario [name]:                     │
│ Recommended drawdown:  X.XX MMT            │
│ Remaining reserve:     X.XX MMT            │
│ Days bridged:          X.X                 │
│ Uncovered gap:         X.XX MMT            │
│                                            │
│ ⚠ "Modelled SPR support requirement"      │
│   NOT "Government-approved recommendation" │
└────────────────────────────────────────────┘
```

Source: ISPRL official data (capacity). Current levels are estimates unless verified.

---

## Loading / Error / Empty States

| State | UI Behavior |
|---|---|
| **Loading** | Skeleton placeholders with shimmer animation. Never show blank screens. |
| **Error (API down)** | Show last-known data with "Stale data — last updated [timestamp]" banner |
| **Error (LLM unavailable)** | Show cached events; disable "Extract new events" button; show notice |
| **Empty (no events)** | Show "No events detected in this time window" with data source status indicators |
| **Empty (no scenarios run)** | Show preset scenario cards with "Run Scenario" buttons |
| **Demo mode** | Show "DEMO MODE — using fixture data" banner in distinct color |

---

## Real vs Simulated Data Indicators

Every data element in the UI must carry a visual classification tag:

| Tag | Color | Meaning |
|---|---|---|
| `LIVE` | Green badge | Currently fetched from external source |
| `RECENT` | Blue badge | Updated within last 24 hours |
| `HISTORICAL` | Gray badge | Static reference data from public sources |
| `DERIVED` | Orange badge | Calculated from other data |
| `SIMULATED` | Yellow/amber badge with ⚠ | Generated for scenario/demo purposes |

These tags should be:
- Small but visible next to data values
- Consistent across all pages
- Filterable if appropriate (e.g., "show only live data")

---

## Navigation

```
INDRA
├── Risk Overview (landing page)
├── Supply Map
├── Scenario Simulator
├── Procurement
└── [Evidence drawer — accessible from any page via "Why?" links]
```

Navigation should be via a top nav bar or sidebar. The evidence drawer slides in from the right side when any score/recommendation is clicked.

---

## Responsive Design Notes

- Primary target: Desktop/laptop browser (1280px+ width)
- The map and data tables require wide viewport
- Mobile optimization is NOT a Phase 1 requirement
- Minimum supported width: 1024px

---

## CSS Framework Decision

> **CONFLICT:** The INDRA Master Report specifies Tailwind CSS. The user instructions state "Use Vanilla CSS for maximum flexibility and control. Avoid using TailwindCSS unless the USER explicitly requests it."
>
> **Resolution:** This decision is deferred. The implementing agent should confirm with the user before selecting a CSS framework. The UI specification above is framework-agnostic.
