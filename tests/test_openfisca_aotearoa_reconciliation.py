from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION_PATH = (
    ROOT / "data" / "coverage" / "openfisca-aotearoa-reconciliation.json"
)
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "openfisca-aotearoa-source-map.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast(JsonMap, json.loads(path.read_text(encoding="utf-8")))


def load_reconciliation() -> JsonMap:
    return load_json(RECONCILIATION_PATH)


@pytest.mark.unit
def test_reconciliation_closes_track_without_treating_oracle_as_law() -> None:
    reconciliation = load_reconciliation()

    assert reconciliation["status"] == "implemented_pending_review"
    assert reconciliation["canonical_law"] is False
    assert reconciliation["blockers"] == []
    assert "No OpenFisca Python formula" in reconciliation["closeout_policy"]
    assert "is treated as legal authority" in reconciliation["closeout_policy"]


@pytest.mark.unit
def test_pin_mismatch_is_explicitly_reconciled_not_hidden() -> None:
    reconciliation = load_reconciliation()
    pin = reconciliation["pin_reconciliation"]

    assert pin["current_oracle_index_commit"] == reconciliation["oracle_index_commit"]
    assert pin["observed_upstream_head"] == reconciliation["observed_upstream_head"]
    assert pin["current_oracle_index_commit"] != pin["observed_upstream_head"]
    assert pin["decision"] == "retain_current_pin_for_deterministic_fixtures"
    assert pin["follow_on_track"] == "openfisca-aotearoa-pin-reconciliation"


@pytest.mark.unit
def test_reconciliation_covers_every_source_map_surface_once() -> None:
    reconciliation = load_reconciliation()
    source_map = load_json(SOURCE_MAP_PATH)
    reconciled = [surface["id"] for surface in reconciliation["surfaces"]]
    mapped = [surface["id"] for surface in source_map["surfaces"]]

    assert reconciled == mapped
    assert len(reconciled) == len(set(reconciled))


@pytest.mark.unit
def test_implemented_surfaces_reference_existing_rulespec_and_tests() -> None:
    reconciliation = load_reconciliation()

    for surface in reconciliation["surfaces"]:
        if not surface["closeout_status"].startswith("implemented_existing"):
            continue
        for path in surface["rulespec_paths"] + surface["companion_tests"]:
            assert (ROOT / path).exists(), path


@pytest.mark.unit
def test_approved_oracle_fixtures_are_comparison_only_and_point_to_rulespec() -> None:
    reconciliation = load_reconciliation()

    assert len(reconciliation["approved_oracle_fixtures"]) == 2
    for item in reconciliation["approved_oracle_fixtures"]:
        fixture_path = ROOT / item["fixture"]
        destination = ROOT / item["rulespec_destination"]
        fixture = load_json(fixture_path)

        assert fixture_path.exists(), item["fixture"]
        assert destination.exists(), item["rulespec_destination"]
        assert fixture["canonical_law"] is False
        assert fixture["oracle_id"] == "openfisca-aotearoa"
        assert fixture["oracle_commit"] == reconciliation["oracle_index_commit"]


@pytest.mark.unit
def test_deferred_surfaces_have_official_source_next_steps_not_blockers() -> None:
    reconciliation = load_reconciliation()
    surfaces = {surface["id"]: surface for surface in reconciliation["surfaces"]}

    for surface_id in [
        "demographics-and-common-predicates",
        "student-allowance",
        "citizenship-and-immigration",
        "rates-rebates",
        "parental-leave",
        "housing-restructuring-and-social-housing",
        "relationship-status-and-family-law-predicates",
    ]:
        surface = surfaces[surface_id]
        assert surface["closeout_status"] == "deferred_to_official_source_extraction"
        assert surface["official_sources_required"], surface_id
        assert surface["planned_rulespec_paths"], surface_id
        assert "not_a_blocker_reason" in surface, surface_id

    assert reconciliation["next_atomic_tracks"] == [
        "openfisca-aotearoa-pin-reconciliation",
        "common-demographics-and-residence-official-source-extraction",
        "citizenship-immigration-official-source-extraction",
        "relationships-official-source-extraction",
        "student-allowance-official-source-extraction",
        "rates-rebates-official-source-extraction",
        "paid-parental-leave-official-source-extraction",
        "housing-restructuring-social-housing-official-source-extraction",
        "acc-weekly-compensation-official-source-extraction",
        "pae-ora-health-services-official-source-extraction",
    ]
