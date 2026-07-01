from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION_PATH = ROOT / "data" / "coverage" / "policyengine-nz-reconciliation.json"
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "policyengine-nz-source-map.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast("JsonMap", json.loads(path.read_text(encoding="utf-8")))


@pytest.mark.unit
def test_reconciliation_records_track_closeout_without_legal_blockers() -> None:
    reconciliation = load_json(RECONCILIATION_PATH)

    assert reconciliation["track_id"] == "14_policyengine_nz_rule_incorporation"
    assert reconciliation["status"] == "implemented_pending_review"
    assert reconciliation["source_oracle_id"] == "policyengine-nz"
    assert reconciliation["canonical_law"] is False
    assert reconciliation["authority"] == "supporting_reference"
    assert reconciliation["blockers"] == []
    assert "No PolicyEngine formula" in reconciliation["closeout_policy"]


@pytest.mark.unit
def test_reconciliation_surfaces_match_source_map_and_artifacts_exist() -> None:
    reconciliation = load_json(RECONCILIATION_PATH)
    source_map = load_json(SOURCE_MAP_PATH)

    assert [surface["id"] for surface in reconciliation["surfaces"]] == [
        surface["id"] for surface in source_map["surfaces"]
    ]

    for surface in reconciliation["surfaces"]:
        if not surface["closeout_status"].startswith("implemented"):
            continue
        for rel_path in surface["rulespec_paths"] + surface["companion_tests"]:
            assert (ROOT / rel_path).exists(), rel_path


@pytest.mark.unit
def test_supporting_fixtures_are_non_authoritative_and_pinned() -> None:
    reconciliation = load_json(RECONCILIATION_PATH)

    fixtures = reconciliation["approved_supporting_fixtures"]
    assert {fixture["surface_id"] for fixture in fixtures} == {
        "income-tax",
        "acc-earners-levy",
        "working-for-families",
    }

    for fixture in fixtures:
        fixture_path = ROOT / fixture["fixture"]
        payload = load_json(fixture_path)
        assert payload["canonical_law"] is False
        assert payload["authority"] == "supporting_reference"
        assert payload["oracle_index_commit"] == reconciliation["oracle_index_commit"]
        assert payload["rulespec_destination"] == fixture["rulespec_destination"]
        assert payload["upstream_test_path"].startswith(
            "policyengine_nz/tests/policy/baseline/",
        )
        assert payload["scenarios"], fixture["surface_id"]
        for scenario in payload["scenarios"]:
            assert scenario["name"]
            assert scenario["period"]
            assert scenario["inputs"]
            assert scenario["expected_outputs"]
            assert scenario["comparison_scope"].endswith("smoke_only")


@pytest.mark.unit
def test_pin_reconciliation_is_deferred_before_live_head_fixture_refresh() -> None:
    reconciliation = load_json(RECONCILIATION_PATH)
    pin = reconciliation["pin_reconciliation"]

    assert pin["current_oracle_index_commit"] == reconciliation["oracle_index_commit"]
    assert pin["observed_upstream_head"] == reconciliation["observed_upstream_head"]
    assert pin["decision"] == "retain_current_pin_for_deterministic_supporting_fixtures"
    assert pin["follow_on_track"] == "policyengine-nz-pin-reconciliation"
