from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION_PATH = ROOT / "data" / "coverage" / "nztaxmicrosim-reconciliation.json"
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "nztaxmicrosim-source-map.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast("JsonMap", json.loads(path.read_text(encoding="utf-8")))


def load_reconciliation() -> JsonMap:
    return load_json(RECONCILIATION_PATH)


@pytest.mark.unit
def test_reconciliation_closes_track_without_treating_oracle_as_law() -> None:
    reconciliation = load_reconciliation()

    assert reconciliation["status"] == "implemented_pending_review"
    assert reconciliation["canonical_law"] is False
    assert reconciliation["blockers"] == []
    assert (
        "No nztaxmicrosim Python formula is treated as legal authority"
        in reconciliation["closeout_policy"]
    )


@pytest.mark.unit
def test_reconciliation_covers_every_source_map_surface_once() -> None:
    reconciliation = load_reconciliation()
    source_map = load_json(SOURCE_MAP_PATH)
    reconciled = [surface["id"] for surface in reconciliation["surfaces"]]
    mapped = [surface["id"] for surface in source_map["surfaces"]]

    assert set(reconciled) == set(mapped)
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
        assert fixture["oracle_id"] == "nztaxmicrosim"


@pytest.mark.unit
def test_deferred_surfaces_have_official_source_next_steps_not_blockers() -> None:
    reconciliation = load_reconciliation()
    surfaces = {surface["id"]: surface for surface in reconciliation["surfaces"]}

    for surface_id in [
        "payroll-deductions",
        "paid-parental-leave",
        "investment-and-withholding-tax",
        "child-support",
    ]:
        surface = surfaces[surface_id]
        assert surface["closeout_status"].startswith("deferred"), surface_id
        assert surface["official_sources_required"], surface_id
        assert surface["planned_rulespec_paths"], surface_id
        assert "not_a_blocker_reason" in surface, surface_id

    assert (
        "simplified"
        in surfaces["investment-and-withholding-tax"]["not_a_blocker_reason"]
    )
    assert "simplified" in surfaces["child-support"]["not_a_blocker_reason"]
    assert reconciliation["next_atomic_tracks"] == [
        "payroll-deductions-official-source-extraction",
        "paid-parental-leave-official-source-extraction",
        "pie-rwt-official-source-extraction",
        "child-support-official-formula-extraction",
    ]
