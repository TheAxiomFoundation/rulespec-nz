from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
ORACLE_INDEX_PATH = ROOT / "data" / "oracles" / "oracle-index.json"
RECONCILIATION_PATH = (
    ROOT / "data" / "coverage" / "openfisca-aotearoa-reconciliation.json"
)
PIN_AUDIT_PATH = ROOT / "data" / "coverage" / "openfisca-aotearoa-pin-audit.json"
INVENTORY_PATH = ROOT / "data" / "oracles" / "openfisca-aotearoa-rule-inventory.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast(JsonMap, json.loads(path.read_text(encoding="utf-8-sig")))


def get_openfisca_oracle() -> JsonMap:
    index = load_json(ORACLE_INDEX_PATH)
    for oracle in index["oracles"]:
        if oracle["id"] == "openfisca-aotearoa":
            return oracle
    msg = "openfisca-aotearoa oracle not found in oracle-index.json"
    raise AssertionError(msg)


@pytest.mark.unit
def test_pin_audit_file_exists() -> None:
    """The pin audit must exist and record reconciled pin state."""
    assert PIN_AUDIT_PATH.exists(), (
        "Pin audit file missing; run Phase 1 of Track 15 to generate it."
    )


@pytest.mark.unit
def test_pin_audit_has_required_fields() -> None:
    """Validate that the pin audit records all required reconciliation fields."""
    audit = load_json(PIN_AUDIT_PATH)

    assert audit["track_id"] == "15_openfisca_follow_on_reconciliation"
    assert "generated_at" in audit
    assert isinstance(audit["generated_at"], str)

    pin = audit["pin_reconciliation"]
    assert pin["source_oracle_id"] == "openfisca-aotearoa"
    assert (
        pin["source_repository"] == "https://github.com/edithatogo/openfisca-aotearoa"
    )
    assert pin["oracle_index_commit"] == "c36c40bcf553dc95ddca473be12440d4be9d0560"
    assert pin["observed_upstream_head"] == "76062ffc20e40373d9cb56c8910a224236aa1e72"
    assert pin["pins_differ"] is True


@pytest.mark.unit
def test_pin_audit_consistent_with_index() -> None:
    """Pin audit commit must match the oracle-index.json entry."""
    audit = load_json(PIN_AUDIT_PATH)
    openfisca = get_openfisca_oracle()

    audit_pin = audit["pin_reconciliation"]["oracle_index_commit"]
    assert audit_pin == openfisca["commit"], (
        f"Pin audit commit {audit_pin} differs from oracle-index {openfisca['commit']}"
    )


@pytest.mark.unit
def test_pin_audit_consistent_with_reconciliation() -> None:
    """Pin audit must be consistent with the reconciliation manifest."""
    audit = load_json(PIN_AUDIT_PATH)
    reconciliation = load_json(RECONCILIATION_PATH)

    audit_pin = audit["pin_reconciliation"]
    reco_pin = reconciliation["pin_reconciliation"]

    assert audit_pin["oracle_index_commit"] == reco_pin["current_oracle_index_commit"]
    assert audit_pin["observed_upstream_head"] == reco_pin["observed_upstream_head"]


@pytest.mark.unit
def test_pin_audit_consistent_with_inventory() -> None:
    """Pin audit must be consistent with the rule inventory."""
    audit = load_json(PIN_AUDIT_PATH)
    inventory = load_json(INVENTORY_PATH)

    assert (
        audit["pin_reconciliation"]["oracle_index_commit"]
        == inventory["oracle_index_commit"]
    )
    assert (
        audit["pin_reconciliation"]["observed_upstream_head"]
        == inventory["observed_upstream_head"]
    )


@pytest.mark.unit
def test_pin_audit_records_upstream_analysis() -> None:
    """The pin audit should contain analysis of what changed upstream."""
    audit = load_json(PIN_AUDIT_PATH)

    analysis = audit.get("upstream_analysis", {})
    assert analysis, "upstream_analysis section is empty"
    assert "divergence_summary" in analysis
    assert "deferred_surfaces_affected" in analysis
    assert isinstance(analysis["deferred_surfaces_affected"], list)
    assert len(analysis["deferred_surfaces_affected"]) > 0


@pytest.mark.unit
def test_pin_audit_decision_is_recorded() -> None:
    """The pin audit must record a decision about the pin."""
    audit = load_json(PIN_AUDIT_PATH)
    decision = audit.get("decision", {})

    assert decision, "decision section is empty"
    assert "action" in decision
    assert decision["action"] in ("retain_pin", "upgrade_pin", "defer_decision")
    assert "rationale" in decision
    assert "follow_on_task" in decision
