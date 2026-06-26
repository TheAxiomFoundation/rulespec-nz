from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any, cast

import pytest


ROOT = Path(__file__).resolve().parents[1]
EXTRACTION_PATH = (
    ROOT / "data" / "coverage" / "openfisca-aotearoa-extraction-verification.json"
)
SOURCE_LOCATOR_PATH = (
    ROOT / "data" / "coverage" / "openfisca-aotearoa-source-locator.json"
)
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
    "acc-and-weekly-compensation",
    "health-and-community-services",
]


@pytest.mark.unit
def test_extraction_verification_file_exists() -> None:
    """The extraction verification document must exist."""
    assert EXTRACTION_PATH.exists(), "Extraction verification missing; run Phase 2 of Track 15."


@pytest.mark.unit
def test_extraction_verification_has_track_metadata() -> None:
    """The verification records track and generation metadata."""
    doc = load_json(EXTRACTION_PATH)
    assert doc["track_id"] == "15_openfisca_follow_on_reconciliation"
    assert "generated_at" in doc
    assert "purpose" in doc


@pytest.mark.unit
def test_extraction_verification_covers_all_deferred_surfaces() -> None:
    """Every deferred surface from the source locator has an extraction verification entry."""
    doc = load_json(EXTRACTION_PATH)
    ver_ids = {entry["surface_id"] for entry in doc["verification_results"]}
    for sid in DEFERRED_SURFACE_IDS:
        assert sid in ver_ids, f"Missing extraction verification for {sid}"


@pytest.mark.unit
def test_each_verification_has_required_fields() -> None:
    """Each verification entry must have surface_id, extraction_approach, and sources."""
    doc = load_json(EXTRACTION_PATH)
    for entry in doc["verification_results"]:
        assert entry["surface_id"], "surface_id required"
        assert entry["extraction_approach"], "extraction_approach required"
        assert entry["sources"], "sources required"
        for src in entry["sources"]:
            assert src["source_name"], "source_name required"
            assert src["pco_status"] in ("exact_match", "exact_match_via_amendments", "related_matches", "not_found"), (
                f"Unknown pco_status: {src['pco_status']}"
            )


@pytest.mark.unit
def test_extraction_verification_consistent_with_source_locator() -> None:
    """Extraction verification surface IDs must match the source locator."""
    doc = load_json(EXTRACTION_PATH)
    locator = load_json(SOURCE_LOCATOR_PATH)
    locator_ids = {entry["surface_id"] for entry in locator["deferred_surfaces"]}
    ver_ids = {entry["surface_id"] for entry in doc["verification_results"]}
    assert ver_ids == locator_ids, (
        f"Surface IDs differ. In ver not in loc: {ver_ids - locator_ids}. "
        f"In loc not in ver: {locator_ids - ver_ids}"
    )


@pytest.mark.unit
def test_extraction_verification_has_summary() -> None:
    """The document must include an extraction summary with totals."""
    doc = load_json(EXTRACTION_PATH)
    summary = doc.get("extraction_summary", {})
    assert summary, "extraction_summary section required"
    assert summary["total_surfaces"] == 9
    assert summary["pco_corpus_available"] == 9
    assert "fallback_required" in summary
    assert summary["fallback_required"] is False


@pytest.mark.unit
def test_extraction_verification_has_baseline() -> None:
    """The document must include an extraction baseline."""
    doc = load_json(EXTRACTION_PATH)
    baseline = doc.get("extraction_baseline", {})
    assert baseline, "extraction_baseline section required"
    assert "corpus_ref" in baseline
    assert "corpus_date" in baseline
    assert "source_map" in baseline


@pytest.mark.unit
def test_each_source_has_pco_document_id() -> None:
    """Each source entry must have a source_document_id."""
    doc = load_json(EXTRACTION_PATH)
    for entry in doc["verification_results"]:
        for src in entry["sources"]:
            assert src["source_document_id"], (
                f"Missing source_document_id for {src['source_name']} in {entry['surface_id']}"
            )


@pytest.mark.unit
def test_all_blockers_are_documented() -> None:
    """External agency blockers must be documented when applicable."""
    doc = load_json(EXTRACTION_PATH)
    for entry in doc["verification_results"]:
        blockers = entry.get("blockers", [])
        assert isinstance(blockers, list), f"blockers must be a list for {entry['surface_id']}"