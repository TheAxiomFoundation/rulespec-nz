from __future__ import annotations

from pathlib import Path

from programs.nz.openfisca_adapter import build_openfisca_reference_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_openfisca_manifest_uses_pinned_oracle_commit_and_is_not_authority() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)

    assert manifest["oracle"]["id"] == "openfisca-aotearoa"
    assert manifest["oracle"]["commit"] == "c36c40bcf553dc95ddca473be12440d4be9d0560"
    assert manifest["canonical_law"] is False
    assert manifest["authority"] == "comparison_oracle"


def test_openfisca_manifest_groups_track_references_with_files() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)
    tracks = {track["track_id"]: track for track in manifest["tracks"]}

    assert "tax-personal-income" in tracks
    assert "openfisca_aotearoa/variables/acts/income_tax/individual.py" in tracks[
        "tax-personal-income"
    ]["files"]
    assert all(track["files"] for track in tracks.values())
    assert all(track["canonical_law"] is False for track in tracks.values())