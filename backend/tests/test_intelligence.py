import pytest

from app.intelligence import StructuredEvent, calculate_risk, rank_procurement, scenario_supply_gap


def test_structured_event_rejects_database_ids():
    with pytest.raises(ValueError):
        StructuredEvent(title="x", event_type="OTHER", severity=5, country_names=[1], confidence=0.9)


def test_risk_formula_and_thresholds_are_deterministic():
    result = calculate_risk({"event_severity": 1, "event_recency": 1, "chokepoint_exposure": 1, "conflict_sanctions": 1, "historical_rate": 1, "india_dependency": 1})
    assert result.score == pytest.approx(1.0)
    assert result.display_score == pytest.approx(100.0)
    assert result.risk_level == "EXTREME"


def test_scenario_and_optimizer_semantics_and_constraints():
    result = scenario_supply_gap("HORMUZ_FULL", 30, 100)
    assert result["supply_gap_mmt"] == pytest.approx(7.056)
    assert result["data_semantic"] == "DERIVED"
    ranked = rank_procurement([{"id": 1, "available_volume": 2, "unit_cost": 10, "risk_score": 0.1, "compatibility_score": .9}, {"id": 2, "available_volume": 2, "unit_cost": 1, "risk_score": 0.1, "compatibility_score": .9, "is_sanctioned": True}], 3)
    assert ranked["feasible"] is False and ranked["selected"][0]["candidate_id"] == 1
