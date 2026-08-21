"""Step 7A — E2E API verification against the live backend.
Tests the full pipeline: EVENT → EXTRACTION → ENTITY RESOLUTION → RISK → SCENARIO → PROCUREMENT → EVIDENCE
"""
import asyncio
import json
import sys
sys.path.insert(0, "backend")

from httpx import ASGITransport, AsyncClient
from app.main import app


async def main():
    results = {"passed": 0, "failed": 0, "errors": []}

    def check(name, condition, detail=""):
        if condition:
            results["passed"] += 1
            print(f"  [PASS] {name}")
        else:
            results["failed"] += 1
            results["errors"].append(f"{name}: {detail}")
            print(f"  [FAIL] {name} — {detail}")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        # --- 1. Health ---
        print("\n=== Health ===")
        r = await client.get("/health")
        check("GET /health → 200", r.status_code == 200, f"got {r.status_code}")
        health = r.json()
        check("health.database = connected", health.get("database") == "connected", health.get("database"))
        check("health.status = ok", health.get("status") == "ok")

        # --- 2. Domain reference endpoints ---
        print("\n=== Domain Reference ===")
        for endpoint, expected_min in [("/countries", 15), ("/corridors", 6), ("/crude-grades", 14),
                                        ("/suppliers", 8), ("/routes", 15), ("/refineries", 20)]:
            r = await client.get(endpoint)
            data = r.json()
            count = len(data) if isinstance(data, list) else 0
            check(f"GET {endpoint} → {count} >= {expected_min}", count >= expected_min, f"got {count}")

        # Reserves
        r = await client.get("/reserves")
        reserves = r.json()
        check("GET /reserves → 3 locations", len(reserves.get("locations", [])) == 3, f"got {len(reserves.get('locations', []))}")
        check("reserves.total_capacity_mmt > 0", float(reserves.get("total_capacity_mmt", 0)) > 0)
        check("reserves.total_current_mmt is None (not fabricated)", reserves.get("total_current_mmt") is None)

        # --- 3. Corridors risk ---
        print("\n=== Corridor Risk ===")
        r = await client.get("/corridors/risk")
        risk_data = r.json()
        items = risk_data.get("items", [])
        check("GET /corridors/risk → items exist", len(items) >= 6, f"got {len(items)}")
        hormuz = next((c for c in items if c["code"] == "HORMUZ"), None)
        check("Hormuz corridor found", hormuz is not None)
        if hormuz:
            check("Hormuz display_score = 60.0", hormuz["display_score"] == 60.0, f"got {hormuz['display_score']}")
            check("Hormuz risk_level = HIGH (not DERIVED)", hormuz["risk_level"] == "HIGH", f"got {hormuz['risk_level']}")
            check("Hormuz data_semantic = OBSERVED", hormuz["data_semantic"] == "OBSERVED")

        # --- 4. Event feed (empty expected) ---
        print("\n=== Events ===")
        r = await client.get("/events")
        events = r.json()
        check("GET /events → items list", "items" in events)
        check("events.data_semantic = OBSERVED", events.get("data_semantic") == "OBSERVED")

        # --- 5. POST /events (entity resolution) ---
        print("\n=== Event Processing + Entity Resolution ===")
        event_payload = {
            "title": "Houthi attack on Red Sea shipping",
            "event_type": "ATTACK",
            "severity": 7,
            "country_names": ["India", "Iraq", "Atlantis"],
            "corridor_names": ["Strait of Hurmuz", "Red Sea"],
            "route_names": [],
            "confidence": 0.85
        }
        r = await client.post("/events", json=event_payload)
        check("POST /events → 200", r.status_code == 200, f"got {r.status_code}")
        result = r.json()
        resolved = result.get("resolved", {})
        unresolved = result.get("unresolved", {})
        check("Iraq resolved as country", any(c.get("name") == "Iraq" for c in resolved.get("countries", [])))
        check("India resolved as country", any(c.get("name") == "India" for c in resolved.get("countries", [])))
        check("Atlantis unresolved", "Atlantis" in unresolved.get("countries", []))
        check("Strait of Hurmuz fuzzy-resolved to corridor", any(c.get("name") == "Strait of Hurmuz" for c in resolved.get("corridors", [])))
        check("Red Sea resolved to corridor", any(c.get("name") == "Red Sea" for c in resolved.get("corridors", [])))
        check("Evidence chain present", "evidence" in result)
        evidence = result.get("evidence", [])
        check("Evidence has source stage", any(e.get("stage") == "source" for e in evidence))
        check("Evidence has extraction stage", any(e.get("stage") == "extraction" for e in evidence))

        # --- 6. Risk calculation ---
        print("\n=== Risk Calculation ===")
        risk_payload = {
            "features": {
                "event_severity": 0.7,
                "event_recency": 0.8,
                "chokepoint_exposure": 0.6,
                "conflict_sanctions": 0.4,
                "historical_rate": 0.3,
                "india_dependency": 0.8
            }
        }
        r = await client.post("/risk", json=risk_payload)
        check("POST /risk → 200", r.status_code == 200, f"got {r.status_code}")
        risk = r.json()
        check("risk.score in 0.0-1.0", 0.0 <= risk.get("score", -1) <= 1.0, f"got {risk.get('score')}")
        check("risk.display_score in 0-100", 0 <= risk.get("display_score", -1) <= 100)
        check("risk.risk_level is valid", risk.get("risk_level") in ("LOW", "MODERATE", "HIGH", "CRITICAL", "EXTREME"))
        check("risk.data_semantic = DERIVED", risk.get("data_semantic") == "DERIVED")
        check("risk.components has all 6 keys", len(risk.get("components", {})) == 6)

        # Determinism check
        r2 = await client.post("/risk", json=risk_payload)
        risk2 = r2.json()
        check("Risk is deterministic (same input → same output)", risk["score"] == risk2["score"])

        # --- 7. Scenario simulation ---
        print("\n=== Scenario Simulation ===")
        scenario_payload = {"scenario_type": "HORMUZ_FULL", "duration_days": 30, "reduction_pct": 100}
        r = await client.post("/scenarios", json=scenario_payload)
        check("POST /scenarios → 200", r.status_code == 200, f"got {r.status_code}")
        scenario = r.json()
        check("scenario.supply_gap_mmt ≈ 7.056", abs(scenario.get("supply_gap_mmt", 0) - 7.056) < 0.01, f"got {scenario.get('supply_gap_mmt')}")
        check("scenario.data_semantic = DERIVED", scenario.get("data_semantic") == "DERIVED")

        # Zero-duration check
        r = await client.post("/scenarios", json={"scenario_type": "HORMUZ_FULL", "duration_days": 0})
        check("0-day scenario → 0 gap", r.json().get("supply_gap_mmt", -1) == 0)

        # Partial closure
        r = await client.post("/scenarios", json={"scenario_type": "HORMUZ_PARTIAL", "duration_days": 30, "reduction_pct": 50})
        partial = r.json()
        check("50% Hormuz → half gap of 100%", abs(partial["supply_gap_mmt"] - 7.056/2) < 0.01, f"got {partial['supply_gap_mmt']}")

        # Russia loss
        r = await client.post("/scenarios", json={"scenario_type": "RUSSIA_LOSS", "duration_days": 30})
        russia = r.json()
        check("Russia loss uses ~37% share", abs(russia["supply_gap_mmt"] - 0.56 * 0.37 * 30) < 0.1, f"got {russia['supply_gap_mmt']}")

        # Invalid scenario
        r = await client.post("/scenarios", json={"scenario_type": "HORMUZ_FULL", "duration_days": -1})
        check("Invalid scenario → 422", r.status_code == 422, f"got {r.status_code}")

        # --- 8. Procurement ---
        print("\n=== Procurement ===")
        procurement_payload = {
            "target_volume": 3,
            "candidates": [
                {"id": 1, "available_volume": 2, "unit_cost": 10, "risk_score": 0.1, "compatibility_score": 0.9, "is_operational": True},
                {"id": 2, "available_volume": 5, "unit_cost": 15, "risk_score": 0.2, "compatibility_score": 0.8, "is_operational": True},
                {"id": 3, "available_volume": 3, "unit_cost": 5, "risk_score": 0.1, "compatibility_score": 0.3},
                {"id": 4, "available_volume": 2, "unit_cost": 8, "risk_score": 0.1, "compatibility_score": 0.9, "is_sanctioned": True},
            ]
        }
        r = await client.post("/recommendations", json=procurement_payload)
        check("POST /recommendations → 200", r.status_code == 200, f"got {r.status_code}")
        rec = r.json()
        check("recommendation.feasible = True", rec.get("feasible") is True)
        check("recommendation.method = deterministic_ranking", rec.get("method") == "deterministic_ranking")
        selected_ids = [s["candidate_id"] for s in rec.get("selected", [])]
        check("Sanctioned supplier (id=4) excluded", 4 not in selected_ids, f"selected: {selected_ids}")
        check("Low-compatibility (id=3) excluded", 3 not in selected_ids, f"selected: {selected_ids}")
        check("Selected items have data_semantic = DERIVED", all(s.get("data_semantic") == "DERIVED" for s in rec.get("selected", [])))

        # --- 9. Route filtering ---
        print("\n=== Route Filtering ===")
        r = await client.get("/routes?corridor=HORMUZ")
        check("GET /routes?corridor=HORMUZ → 200", r.status_code == 200)
        hormuz_routes = r.json()
        check("Hormuz routes found", len(hormuz_routes) > 0, f"got {len(hormuz_routes)}")

        r = await client.get("/routes?corridor=NOT_A_CORRIDOR")
        check("GET /routes?corridor=NOT_A_CORRIDOR → 404", r.status_code == 404)

        # --- 10. CORS check ---
        print("\n=== CORS ===")
        r = await client.options("/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
        check("CORS preflight responds", r.status_code in (200, 204, 405))

        # --- 11. GET /risk summary ---
        print("\n=== Risk Summary ===")
        r = await client.get("/risk")
        check("GET /risk → 200", r.status_code == 200)
        check("GET /risk has data_semantic", r.json().get("data_semantic") == "DERIVED")

    # --- Summary ---
    print("\n" + "=" * 60)
    print(f"E2E VERIFICATION: {results['passed']} passed, {results['failed']} failed")
    print("=" * 60)
    if results["errors"]:
        for e in results["errors"]:
            print(f"  [FAIL] {e}")
    return results["failed"]


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
