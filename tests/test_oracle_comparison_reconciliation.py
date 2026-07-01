from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_EVIDENCE_PATH = (
    ROOT
    / "conductor"
    / "tracks"
    / "archive"
    / "37_oracle_comparison_and_historical_rule_reconciliation"
    / "source-evidence.md"
)
RECONCILIATION_PATHS = {
    "nztaxmicrosim": ROOT / "data" / "coverage" / "nztaxmicrosim-reconciliation.json",
    "openfisca-aotearoa": ROOT
    / "data"
    / "coverage"
    / "openfisca-aotearoa-reconciliation.json",
    "policyengine-nz": ROOT / "data" / "coverage" / "policyengine-nz-reconciliation.json",
}


@pytest.mark.unit
def test_oracle_comparison_manifests_are_pinned_and_non_authoritative() -> None:
    source_evidence = SOURCE_EVIDENCE_PATH.read_text(encoding="utf-8")

    for oracle_id, path in RECONCILIATION_PATHS.items():
        payload = json.loads(path.read_text(encoding="utf-8"))

        assert path.exists(), oracle_id
        assert payload["status"] == "implemented_pending_review"
        assert payload["canonical_law"] is False
        assert payload["blockers"] == []
        assert payload["source_oracle_id"] == oracle_id
        assert path.name in source_evidence


@pytest.mark.unit
def test_oracle_comparison_track_evidence_points_to_the_reconciliation_workflow() -> None:
    source_evidence = SOURCE_EVIDENCE_PATH.read_text(encoding="utf-8")

    assert "scripts/phase3_reconciliation_workflow.py" in source_evidence
    assert "data/oracles/oracle-index.json" in source_evidence
