from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "oracles" / "openfisca-aotearoa-rule-inventory.json"
TRACK_ROOT = (
    ROOT
    / "conductor"
    / "tracks"
    / "archive"
    / "13_openfisca_aotearoa_rule_incorporation"
)


@pytest.mark.unit
def test_openfisca_inventory_records_pin_mismatch_and_oracle_boundary() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    oracle_index = json.loads(
        (ROOT / "data" / "oracles" / "oracle-index.json").read_text(encoding="utf-8")
    )
    openfisca = next(
        oracle
        for oracle in oracle_index["oracles"]
        if oracle["id"] == "openfisca-aotearoa"
    )

    assert inventory["source_oracle_id"] == "openfisca-aotearoa"
    assert inventory["oracle_index_commit"] == openfisca["commit"]
    assert inventory["observed_upstream_head"] != inventory["oracle_index_commit"]
    assert inventory["canonical_law"] is False
    assert inventory["authority"] == "comparison_oracle"


@pytest.mark.unit
def test_openfisca_inventory_counts_observed_rule_surfaces() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    assert inventory["counts"] == {
        "variable_files": 101,
        "parameter_files": 84,
        "yaml_situation_tests": 72,
    }
    assert inventory["source_surface_counts"]["variables"]["acts"] == 78
    assert inventory["source_surface_counts"]["variable_acts"]["social_security"] == 44
    assert inventory["source_surface_counts"]["parameters"]["social_security"] == 41
    assert inventory["source_surface_counts"]["yaml_tests"]["social_security"] == 39


@pytest.mark.unit
def test_openfisca_inventory_identifies_missing_and_partial_surfaces() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    surfaces = {surface["id"]: surface for surface in inventory["rule_surfaces"]}

    assert surfaces["income-tax-and-family-scheme"]["status"] == "partial"
    assert surfaces["social-security-main-benefits"]["status"] == "partial"
    assert surfaces["student-allowance"]["status"] == "missing"
    assert surfaces["citizenship-and-immigration"]["status"] == "missing"
    assert surfaces["rates-rebates"]["status"] == "missing"
    assert surfaces["parental-leave"]["status"] == "missing"
    assert surfaces["housing-restructuring-and-social-housing"]["status"] == "missing"


@pytest.mark.unit
def test_openfisca_track_requires_pin_reconciliation_before_fixture_import() -> None:
    spec = (TRACK_ROOT / "spec.md").read_text(encoding="utf-8")
    plan = (TRACK_ROOT / "plan.md").read_text(encoding="utf-8")

    assert "data/oracles/openfisca-aotearoa-rule-inventory.json" in spec
    assert "Do not silently update `data/oracles/oracle-index.json`" in spec
    assert "Decide whether to upgrade `data/oracles/oracle-index.json`" in plan
    assert "Keep fixtures labelled `canonical_law: false`" in plan
