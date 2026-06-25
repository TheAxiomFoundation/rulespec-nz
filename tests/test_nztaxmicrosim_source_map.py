from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "nztaxmicrosim-source-map.json"
INVENTORY_PATH = ROOT / "data" / "oracles" / "nztaxmicrosim-rule-inventory.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast(JsonMap, json.loads(path.read_text(encoding="utf-8")))


def load_source_map() -> JsonMap:
    return load_json(SOURCE_MAP_PATH)


@pytest.mark.unit
def test_nztaxmicrosim_source_map_keeps_oracle_non_authoritative() -> None:
    source_map = load_source_map()
    inventory = load_json(INVENTORY_PATH)

    assert source_map["source_oracle_id"] == "nztaxmicrosim"
    assert source_map["source_commit"] == inventory["source_commit"]
    assert source_map["canonical_law"] is False
    assert source_map["authority"] == "comparison_oracle"
    assert "official NZ legislation" in source_map["official_source_policy"]
    assert "regression fixtures only" in source_map["official_source_policy"]


@pytest.mark.unit
def test_source_map_covers_every_inventory_surface_once() -> None:
    source_map = load_source_map()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    mapped = [surface["id"] for surface in source_map["surfaces"]]
    inventoried = [surface["id"] for surface in inventory["rule_surfaces"]]

    assert mapped == inventoried
    assert len(mapped) == len(set(mapped))


@pytest.mark.unit
def test_existing_surfaces_have_current_rulespec_paths_and_tests() -> None:
    surfaces = {surface["id"]: surface for surface in load_source_map()["surfaces"]}

    for surface_id in [
        "personal-income-tax-history",
        "individual-tax-credits",
        "working-for-families",
        "main-benefits-and-supplements",
        "acc-earners-levy",
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
        "payroll-deductions",
        "investment-and-withholding-tax",
        "paid-parental-leave",
        "child-support",
    ]:
        surface = surfaces[surface_id]
        assert surface["official_sources"], surface_id
        assert surface["planned_rulespec_paths"], surface_id
        assert surface["implementation_status"].startswith("missing"), surface_id

    assert "KiwiSaver Act 2006" in surfaces["payroll-deductions"]["official_sources"]
    assert (
        "Student Loan Scheme Act 2011"
        in surfaces["payroll-deductions"]["official_sources"]
    )
    assert "Child Support Act 1991" in surfaces["child-support"]["official_sources"]


@pytest.mark.unit
def test_simplified_oracle_logic_is_blocked_from_canonical_encoding() -> None:
    surfaces = {surface["id"]: surface for surface in load_source_map()["surfaces"]}

    assert "blockers" in surfaces["working-for-families"]
    assert "blockers" in surfaces["investment-and-withholding-tax"]
    assert "blockers" in surfaces["child-support"]
    assert "simplified" in " ".join(
        surfaces["investment-and-withholding-tax"]["blockers"]
    )
    assert "simplified" in " ".join(surfaces["child-support"]["blockers"])


@pytest.mark.unit
def test_implementation_order_avoids_new_work_before_reconciliation() -> None:
    source_map = load_source_map()
    order = source_map["implementation_order"]

    assert order[:5] == [
        "acc-earners-levy",
        "personal-income-tax-history",
        "individual-tax-credits",
        "working-for-families",
        "main-benefits-and-supplements",
    ]
    assert order[-2:] == ["investment-and-withholding-tax", "child-support"]
