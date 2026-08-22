"""Focused Step-8D-A procurement optimization tests."""
from __future__ import annotations

import pytest

from app.intelligence import optimize_procurement


def candidate(
    ident: int,
    *,
    capacity: float = 5,
    unit_cost: float = 10,
    risk: float = 0.1,
    transit: float = 10,
    compatibility: float = 0.9,
    sanctioned: bool = False,
    operational: bool = True,
    disrupted: bool = False,
    route_capacity: float | None = None,
) -> dict:
    item = {
        "id": ident,
        "supplier_id": 100 + ident,
        "supplier_name": f"Supplier {ident}",
        "crude_grade_id": 200 + ident,
        "crude_grade_name": f"Grade {ident}",
        "route_id": 300 + ident,
        "route_name": f"Route {ident}",
        "available_volume": capacity,
        "unit_cost": unit_cost,
        "risk_score": risk,
        "transit_days": transit,
        "compatibility_score": compatibility,
        "is_sanctioned": sanctioned,
        "is_operational": operational,
        "is_route_disrupted": disrupted,
    }
    if route_capacity is not None:
        item["route_capacity"] = route_capacity
    return item


def test_feasible_lp_returns_selected_entities_and_objective():
    result = optimize_procurement([candidate(1, capacity=2), candidate(2, unit_cost=12)], 3)

    assert result["feasible"] is True
    assert result["solver_status"] == "OPTIMAL"
    assert result["method"] == "scipy_linprog"
    assert result["objective_value"] is not None
    assert sum(item["allocated_volume"] for item in result["selected"]) == pytest.approx(3)
    assert {item["supplier_id"] for item in result["selected"]} == {101, 102}
    assert all(item["crude_grade_id"] and item["route_id"] for item in result["selected"])
    assert result["data_semantic"] == "DERIVED"
    assert result["provenance"]["stage"] == "optimization"


def test_lp_respects_supplier_and_route_capacity():
    result = optimize_procurement(
        [candidate(1, capacity=5, route_capacity=1), candidate(2, capacity=5, route_capacity=5, unit_cost=20)],
        3,
    )

    allocations = {item["candidate_id"]: item["allocated_volume"] for item in result["selected"]}
    assert allocations[1] <= 1 + 1e-9
    assert sum(allocations.values()) == pytest.approx(3)


def test_sanctioned_supplier_is_excluded():
    result = optimize_procurement([candidate(1, sanctioned=True), candidate(2)], 2)

    assert all(item["candidate_id"] != 1 for item in result["selected"])
    assert {item["candidate_id"] for item in result["selected"]} == {2}
    assert {item["reason"] for item in result["constraints"]["excluded_candidates"]} == {"sanctioned_supplier"}


def test_disrupted_or_non_operational_route_is_excluded():
    result = optimize_procurement([candidate(1, disrupted=True), candidate(2, operational=False), candidate(3)], 2)

    assert {item["candidate_id"] for item in result["selected"]} == {3}
    reasons = {item["candidate_id"]: item["reason"] for item in result["constraints"]["excluded_candidates"]}
    assert reasons[1] == "route_disrupted"
    assert reasons[2] == "route_not_operational"


def test_compatibility_threshold_excludes_incompatible_grade():
    result = optimize_procurement([candidate(1, compatibility=0.4), candidate(2)], 2, compatibility_threshold=0.5)

    assert {item["candidate_id"] for item in result["selected"]} == {2}
    assert result["constraints"]["excluded_candidates"][0]["reason"] == "incompatible_crude_grade"


def test_target_volume_is_satisfied_exactly_when_feasible():
    result = optimize_procurement([candidate(1, capacity=1), candidate(2, capacity=2)], 2.5)

    assert result["feasible"] is True
    assert result["unmet_volume"] == pytest.approx(0)
    assert sum(item["volume"] for item in result["selected"]) == pytest.approx(2.5)


def test_infeasible_target_is_explicit_and_does_not_claim_feasible():
    result = optimize_procurement([candidate(1, capacity=1), candidate(2, capacity=1)], 5)

    assert result["feasible"] is False
    assert result["solver_status"] == "INFEASIBLE"
    assert result["fallback_used"] is True
    assert result["fallback_reason"].startswith("infeasible:")
    assert result["unmet_volume"] == pytest.approx(3)


def test_incomplete_candidate_uses_existing_deterministic_fallback():
    legacy = {"id": 1, "available_volume": 2, "unit_cost": 10, "risk_score": 0.1, "compatibility_score": 0.9}
    result = optimize_procurement([legacy], 1)

    assert result["solver_status"] == "FALLBACK"
    assert result["fallback_used"] is True
    assert result["method"] == "deterministic_ranking"
    assert result["fallback_reason"] == "candidate_identity_missing"
    assert result["selected"][0]["candidate_id"] == 1


def test_lp_output_is_deterministic():
    candidates = [candidate(1, capacity=2), candidate(2, capacity=2, unit_cost=11)]

    first = optimize_procurement(candidates, 3)
    second = optimize_procurement(candidates, 3)

    assert first == second

