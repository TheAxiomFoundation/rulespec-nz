from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "oracles" / "policyengine-nz-rule-inventory.json"
TRACK_ROOT = (
    ROOT / "conductor" / "tracks" / "archive" / "14_policyengine_nz_rule_incorporation"
)


@pytest.mark.unit
def test_policyengine_inventory_records_pin_mismatch_and_reference_boundary() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    oracle_index = json.loads(
        (ROOT / "data" / "oracles" / "oracle-index.json").read_text(encoding="utf-8"),
    )
    policyengine = next(
        oracle
        for oracle in oracle_index["oracles"]
        if oracle["id"] == "policyengine-nz"
    )

    assert inventory["source_oracle_id"] == "policyengine-nz"
    assert inventory["oracle_index_commit"] == policyengine["commit"]
    assert inventory["observed_upstream_head"] != inventory["oracle_index_commit"]
    assert inventory["canonical_law"] is False
    assert inventory["authority"] == "supporting_reference"


@pytest.mark.unit
def test_policyengine_inventory_counts_observed_rule_surfaces() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    assert inventory["counts"] == {
        "variable_files": 17,
        "parameter_files": 14,
        "yaml_policy_tests": 3,
    }
    assert inventory["source_surface_counts"]["variable_gov"]["ird/income_tax"] == 2
    assert (
        inventory["source_surface_counts"]["variable_gov"]["ird/working_for_families"]
        == 3
    )
    assert (
        inventory["source_surface_counts"]["parameters_gov"]["ird/working_for_families"]
        == 4
    )
    assert inventory["source_surface_counts"]["yaml_tests"]["policy/baseline"] == 3


@pytest.mark.unit
def test_policyengine_inventory_identifies_missing_and_reconcile_surfaces() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    surfaces = {surface["id"]: surface for surface in inventory["rule_surfaces"]}

    assert surfaces["income-tax"]["status"] == "partial"
    assert surfaces["working-for-families"]["status"] == "partial"
    assert surfaces["acc-earners-levy"]["status"] == "covered_reconcile"
    assert surfaces["gst"]["status"] == "covered_reconcile"
    assert surfaces["kiwisaver"]["status"] == "missing"


@pytest.mark.unit
def test_policyengine_track_requires_pin_reconciliation_before_fixture_import() -> None:
    spec = (TRACK_ROOT / "spec.md").read_text(encoding="utf-8")
    plan = (TRACK_ROOT / "plan.md").read_text(encoding="utf-8")

    assert "data/oracles/policyengine-nz-rule-inventory.json" in spec
    assert "Do not silently update `data/oracles/oracle-index.json`" in spec
    assert "Decide whether to upgrade `data/oracles/oracle-index.json`" in plan
    assert "supporting reference evidence" in plan
