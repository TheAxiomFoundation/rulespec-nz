from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "oracles" / "nztaxmicrosim-rule-inventory.json"
TRACK_ROOT = (
    ROOT / "conductor" / "tracks" / "archive" / "12_nztaxmicrosim_rule_incorporation"
)


@pytest.mark.unit
def test_nztaxmicrosim_inventory_uses_pinned_oracle_boundary() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    oracle_index = json.loads(
        (ROOT / "data" / "oracles" / "oracle-index.json").read_text(encoding="utf-8"),
    )
    nztaxmicrosim = next(
        oracle for oracle in oracle_index["oracles"] if oracle["id"] == "nztaxmicrosim"
    )

    assert inventory["source_oracle_id"] == "nztaxmicrosim"
    assert inventory["source_commit"] == nztaxmicrosim["commit"]
    assert inventory["canonical_law"] is False
    assert inventory["authority"] == "comparison_oracle"


@pytest.mark.unit
def test_nztaxmicrosim_inventory_covers_rule_bearing_modules() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    modules = {module["path"] for module in inventory["source_modules"]}

    assert {
        "src/tax_rules.py",
        "src/tax_calculator.py",
        "src/tax_credits.py",
        "src/wff_rules.py",
        "src/benefit_rules.py",
        "src/benefits.py",
        "src/acc_levy.py",
        "src/payroll_deductions.py",
        "src/investment_tax.py",
        "src/historical_data.py",
        "src/data/nz_personal_tax_rules.json",
        "src/data/nz_personal_tax_full.json",
        "src/data/parameters.db",
    } <= modules


@pytest.mark.unit
def test_nztaxmicrosim_inventory_identifies_missing_rulespec_surfaces() -> None:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    surfaces = {surface["id"]: surface for surface in inventory["rule_surfaces"]}

    assert surfaces["payroll-deductions"]["status"] == "missing"
    assert surfaces["investment-and-withholding-tax"]["status"] == "missing"
    assert surfaces["paid-parental-leave"]["status"] == "missing"
    assert surfaces["child-support"]["status"] == "missing"
    assert surfaces["acc-earners-levy"]["status"] == "covered_reconcile"


@pytest.mark.unit
def test_nztaxmicrosim_track_links_inventory_and_oracle_limitations() -> None:
    spec = (TRACK_ROOT / "spec.md").read_text(encoding="utf-8")
    plan = (TRACK_ROOT / "plan.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK_ROOT / "metadata.json").read_text(encoding="utf-8"))

    assert metadata["status"] == "archived_after_review_remediation"
    assert metadata["review_complete"] is True
    assert "data/oracles/nztaxmicrosim-rule-inventory.json" in spec
    assert "Do not copy `nztaxmicrosim` Python functions mechanically" in spec
    assert "official-source extraction" in plan
    assert "Archive Track 12 after review remediation" in plan
