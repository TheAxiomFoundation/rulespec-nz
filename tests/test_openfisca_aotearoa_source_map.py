from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "openfisca-aotearoa-source-map.json"
INVENTORY_PATH = ROOT / "data" / "oracles" / "openfisca-aotearoa-rule-inventory.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast(JsonMap, json.loads(path.read_text(encoding="utf-8")))


def load_source_map() -> JsonMap:
    return load_json(SOURCE_MAP_PATH)


@pytest.mark.unit
def test_openfisca_source_map_keeps_oracle_non_authoritative() -> None:
    source_map = load_source_map()
    inventory = load_json(INVENTORY_PATH)

    assert source_map["source_oracle_id"] == "openfisca-aotearoa"
    assert source_map["oracle_index_commit"] == inventory["oracle_index_commit"]
    assert source_map["observed_upstream_head"] == inventory["observed_upstream_head"]
    assert source_map["canonical_law"] is False
    assert source_map["authority"] == "comparison_oracle"
    assert "official NZ legislation" in source_map["official_source_policy"]
    assert "situation-test fixtures only" in source_map["official_source_policy"]


@pytest.mark.unit
def test_pin_mismatch_is_recorded_as_separate_fixture_extraction_gate() -> None:
    source_map = load_source_map()

    assert source_map["observed_upstream_head"] != source_map["oracle_index_commit"]
    assert "oracle-index commit" in source_map["pin_policy"]
    assert "separate pin-reconciliation task" in source_map["pin_policy"]
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
        "income-tax-and-family-scheme",
        "social-security-main-benefits",
        "accommodation-supplement",
        "acc-and-weekly-compensation",
        "health-and-community-services",
    ]:
        surface = surfaces[surface_id]
        assert surface["existing_rulespec_paths"], surface_id
        assert surface["companion_tests"], surface_id
        for path in surface["existing_rulespec_paths"] + surface["companion_tests"]:
            assert (ROOT / path).exists(), path


@pytest.mark.unit
def test_missing_surfaces_have_official_sources_and_planned_destinations() -> None:
    surfaces = {surface["id"]: surface for surface in load_source_map()["surfaces"]}

    for surface_id in [
        "student-allowance",
        "citizenship-and-immigration",
        "rates-rebates",
        "parental-leave",
        "housing-restructuring-and-social-housing",
        "relationship-status-and-family-law-predicates",
    ]:
        surface = surfaces[surface_id]
        assert surface["implementation_status"] == "missing_ready_for_source_extraction"
        assert surface["official_sources"], surface_id
        assert surface["planned_rulespec_paths"], surface_id

    assert (
        "Student Allowances Regulations 1998"
        in surfaces["student-allowance"]["official_sources"]
    )
    assert "Rates Rebate Act 1973" in surfaces["rates-rebates"]["official_sources"]
    assert (
        "Housing Restructuring and Tenancy Matters Act 1992"
        in surfaces["housing-restructuring-and-social-housing"]["official_sources"]
    )


@pytest.mark.unit
def test_implementation_order_reconciles_existing_coverage_before_new_surfaces() -> (
    None
):
    order = load_source_map()["implementation_order"]

    assert order[:5] == [
        "income-tax-and-family-scheme",
        "social-security-main-benefits",
        "accommodation-supplement",
        "acc-and-weekly-compensation",
        "health-and-community-services",
    ]
    assert order[-4:] == [
        "student-allowance",
        "rates-rebates",
        "parental-leave",
        "housing-restructuring-and-social-housing",
    ]
