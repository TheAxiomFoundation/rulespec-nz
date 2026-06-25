from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "policyengine-nz-source-map.json"
INVENTORY_PATH = ROOT / "data" / "oracles" / "policyengine-nz-rule-inventory.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast(JsonMap, json.loads(path.read_text(encoding="utf-8")))


def load_source_map() -> JsonMap:
    return load_json(SOURCE_MAP_PATH)


@pytest.mark.unit
def test_policyengine_source_map_keeps_reference_non_authoritative() -> None:
    source_map = load_source_map()
    inventory = load_json(INVENTORY_PATH)

    assert source_map["source_oracle_id"] == "policyengine-nz"
    assert source_map["oracle_index_commit"] == inventory["oracle_index_commit"]
    assert source_map["observed_upstream_head"] == inventory["observed_upstream_head"]
    assert source_map["canonical_law"] is False
    assert source_map["authority"] == "supporting_reference"
    assert "official NZ legislation" in source_map["official_source_policy"]
    assert "policy-test fixtures only" in source_map["official_source_policy"]


@pytest.mark.unit
def test_pin_mismatch_is_recorded_as_separate_fixture_extraction_gate() -> None:
    source_map = load_source_map()

    assert source_map["observed_upstream_head"] != source_map["oracle_index_commit"]
    assert "oracle-index commit" in source_map["pin_policy"]
    assert "policyengine-nz-pin-reconciliation" in source_map["pin_policy"]
    assert source_map["global_blockers"] == []


@pytest.mark.unit
def test_source_map_covers_every_inventory_surface_once() -> None:
    source_map = load_source_map()
    inventory = load_json(INVENTORY_PATH)
    mapped = [surface["id"] for surface in source_map["surfaces"]]
    inventoried = [surface["id"] for surface in inventory["rule_surfaces"]]

    assert mapped == inventoried
    assert len(mapped) == len(set(mapped))


@pytest.mark.unit
def test_existing_surfaces_have_current_rulespec_paths_and_tests() -> None:
    surfaces = {surface["id"]: surface for surface in load_source_map()["surfaces"]}

    for surface_id in [
        "income-tax",
        "acc-earners-levy",
        "working-for-families",
        "main-benefits-jobseeker",
        "new-zealand-superannuation",
        "accommodation-supplement",
        "gst",
        "kiwisaver",
    ]:
        surface = surfaces[surface_id]
        assert surface["existing_rulespec_paths"], surface_id
        assert surface["companion_tests"], surface_id
        for rel_path in surface["existing_rulespec_paths"] + surface["companion_tests"]:
            assert (ROOT / rel_path).exists(), rel_path


@pytest.mark.unit
def test_kiwisaver_is_implemented_from_official_sources_not_policyengine() -> None:
    surfaces = {surface["id"]: surface for surface in load_source_map()["surfaces"]}
    kiwisaver = surfaces["kiwisaver"]

    assert kiwisaver["implementation_status"] == "implemented_new_official_source"
    assert (
        "KiwiSaver Act 2006 ss 64, 101B, and schedule 1"
        in kiwisaver["official_sources"]
    )
    assert kiwisaver["existing_rulespec_paths"] == [
        "nz/statutes/kiwisaver/contributions.yaml"
    ]
    assert kiwisaver["companion_tests"] == [
        "nz/statutes/kiwisaver/contributions.test.yaml"
    ]
    assert kiwisaver["oracle_use"] == "supporting contribution-rate discovery only"


@pytest.mark.unit
def test_implementation_order_reconciles_existing_coverage_before_new_kiwisaver() -> (
    None
):
    order = load_source_map()["implementation_order"]

    assert order[:2] == ["acc-earners-levy", "gst"]
    assert order[-1] == "kiwisaver"
