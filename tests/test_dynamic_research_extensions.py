from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "analysis" / "dynamic-research-extensions.json"
ORACLE_INDEX_PATH = ROOT / "data" / "oracles" / "oracle-index.json"


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


@pytest.mark.unit
def test_dynamic_research_manifest_is_pinned_and_research_only() -> None:
    manifest = _load_json(MANIFEST_PATH)

    assert manifest["track_id"] == "39_dynamic_simulation_and_research_extensions"
    assert manifest["status"] == "implemented_pending_review"
    assert manifest["scope"] == "research_only"
    assert manifest["research_checks"] == [
        "research_bucket_remains_separate_from_legislation_tracks",
        "references_existing_encoded_surfaces_without_duplication",
        "keeps_live_workflows_external_and_optional",
    ]
    assert manifest["linked_repository_contracts"][0]["id"] == "regression-voi-pipeline"
    assert manifest["linked_repository_contracts"][1]["id"] == "state-ledger-temporal-policy"


@pytest.mark.unit
def test_dynamic_research_manifest_pins_existing_research_oracles() -> None:
    manifest = _load_json(MANIFEST_PATH)
    oracle_index = _load_json(ORACLE_INDEX_PATH)
    oracle_ids = {oracle["id"] for oracle in oracle_index["oracles"]}

    research_oracles = {oracle["id"]: oracle for oracle in manifest["research_oracles"]}

    assert set(research_oracles) == {"kairos", "lifecourse", "voiage", "innovate"}
    assert research_oracles["kairos"]["status"] == "pinned_research_oracle"
    assert research_oracles["voiage"]["status"] == "pinned_research_oracle"
    assert research_oracles["lifecourse"]["status"] == "research_oracle"
    assert research_oracles["innovate"]["status"] == "research_oracle"
    assert set(research_oracles) <= oracle_ids


@pytest.mark.unit
def test_dynamic_research_manifest_keeps_boundary_rules_non_legal() -> None:
    manifest = _load_json(MANIFEST_PATH)

    boundaries = manifest["boundary_rules"]
    assert isinstance(boundaries, dict)
    assert "data/analysis/local/**" in boundaries["never_commit_globs"]
    assert "data/ledger/local/**" in boundaries["never_commit_globs"]
    assert "data/analysis/*.json" in boundaries["allowed_promoted_outputs"]
    assert "data/ledger/*.json" in boundaries["allowed_promoted_outputs"]
