from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_LOCATOR_PATH = (
    ROOT / "data" / "coverage" / "openfisca-aotearoa-source-locator.json"
)
RECONCILIATION_PATH = ROOT / "data" / "coverage" / "openfisca-aotearoa-reconciliation.json"
INVENTORY_PATH = ROOT / "data" / "oracles" / "openfisca-aotearoa-rule-inventory.json"
JsonMap = dict[str, Any]


def load_json(path: Path) -> JsonMap:
    return cast(JsonMap, json.loads(path.read_text(encoding="utf-8-sig")))


DEFERRED_SURFACE_IDS = [
    "demographics-and-common-predicates",
    "citizenship-and-immigration",
    "relationship-status-and-family-law-predicates",
    "student-allowance",
    "rates-rebates",
    "parental-leave",
    "housing-restructuring-and-social-housing",
]

EXPECTED_EXTRACTION_TRACKS = [
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


@pytest.mark.unit
def test_source_locator_file_exists() -> None:
    """The source locator must exist."""
    assert SOURCE_LOCATOR_PATH.exists(), (
        "Source locator missing; run Phase 1 Task 2 of Track 15."
    )


@pytest.mark.unit
def test_source_locator_has_track_metadata() -> None:
    """The source locator records track and generation metadata."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    assert locator["track_id"] == "15_openfisca_follow_on_reconciliation"
    assert "generated_at" in locator
    assert "purpose" in locator


@pytest.mark.unit
def test_source_locator_covers_all_deferred_surfaces() -> None:
    """Every deferred surface from the reconciliation has a source locator entry."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    locator_ids = {entry["surface_id"] for entry in locator["deferred_surfaces"]}
    for sid in DEFERRED_SURFACE_IDS:
        assert sid in locator_ids, f"Missing source locator for {sid}"


@pytest.mark.unit
def test_source_locator_consistent_with_reconciliation() -> None:
    """Source locator surface IDs must match the reconciliation manifest."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    reconciliation = load_json(RECONCILIATION_PATH)
    reconciled_ids = {s["id"] for s in reconciliation["surfaces"]}
    locator_ids = {entry["surface_id"] for entry in locator["deferred_surfaces"]}
    assert locator_ids.issubset(reconciled_ids), (
        f"Unknown surfaces: {locator_ids - reconciled_ids}"
    )


@pytest.mark.unit
def test_source_locator_consistent_with_inventory() -> None:
    """Source locator surface IDs must match the rule inventory."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    inventory = load_json(INVENTORY_PATH)
    inventoried_ids = {s["id"] for s in inventory["rule_surfaces"]}
    locator_ids = {entry["surface_id"] for entry in locator["deferred_surfaces"]}
    assert locator_ids.issubset(inventoried_ids), (
        f"Unknown surfaces: {locator_ids - inventoried_ids}"
    )
@pytest.mark.unit
def test_each_deferred_surface_has_required_fields() -> None:
    """Each deferred surface entry must have all required fields."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    for entry in locator["deferred_surfaces"]:
        assert entry["surface_id"], "surface_id required"
        assert entry["surface_name"], "surface_name required"
        assert entry["status"], "status required"
        assert entry["official_sources"], "official_sources required"
        assert entry["planned_rulespec_paths"], "planned_rulespec_paths required"
        assert entry["extraction_track"], "extraction_track required"
        assert entry["corpus_citation_paths"], "corpus_citation_paths required"

        assert entry["extraction_track"] in EXPECTED_EXTRACTION_TRACKS, (
            f"Unknown extraction track: {entry['extraction_track']}"
        )
        assert len(entry["corpus_citation_paths"]) > 0, (
            f"Empty corpus_citation_paths for {entry['surface_id']}"
        )
        assert len(entry["official_sources"]) > 0, (
            f"Empty official_sources for {entry['surface_id']}"
        )
        assert len(entry["planned_rulespec_paths"]) > 0, (
            f"Empty planned_rulespec_paths for {entry['surface_id']}"
        )


@pytest.mark.unit
def test_source_locator_has_pin_reconciliation_entry() -> None:
    """The source locator must include a pin reconciliation entry."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    pin_entry = locator.get("pin_reconciliation", {})
    assert pin_entry, "pin_reconciliation section required"
    assert pin_entry["oracle_id"] == "openfisca-aotearoa"
    assert pin_entry["current_pin"] == "c36c40bcf553dc95ddca473be12440d4be9d0560"
    assert pin_entry["upstream_head"] == "76062ffc20e40373d9cb56c8910a224236aa1e72"
    assert "decision" in pin_entry
    assert "follow_on_track" in pin_entry
    assert pin_entry["follow_on_track"] == "openfisca-aotearoa-pin-reconciliation"


@pytest.mark.unit
def test_source_locator_has_acc_weekly_compensation_entry() -> None:
    """ACC weekly compensation must have official sources identified."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    surfaces_by_track = {
        entry["extraction_track"]: entry for entry in locator["deferred_surfaces"]
    }
    acc_track = "acc-weekly-compensation-official-source-extraction"
    assert acc_track in surfaces_by_track, f"Missing {acc_track}"
    entry = surfaces_by_track[acc_track]
    assert "Accident Compensation Act 2001" in " ".join(entry["official_sources"]), (
        "ACC must reference Accident Compensation Act 2001"
    )


@pytest.mark.unit
def test_source_locator_has_pae_ora_health_services_entry() -> None:
    """Pae Ora health services must have official sources identified."""
    locator = load_json(SOURCE_LOCATOR_PATH)
    surfaces_by_track = {
        entry["extraction_track"]: entry for entry in locator["deferred_surfaces"]
    }
    pae_track = "pae-ora-health-services-official-source-extraction"
    assert pae_track in surfaces_by_track, f"Missing {pae_track}"
    entry = surfaces_by_track[pae_track]
    assert "Pae Ora" in " ".join(entry["official_sources"]), (
        "Pae Ora must reference Pae Ora (Healthy Futures) Act 2022"
    )