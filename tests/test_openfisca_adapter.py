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
    assert (
        tracks["tax-personal-income"]["source_commit"]
        == manifest["oracle"]["commit"]
    )
    assert "nz/statutes/income_tax/core/taxable_income.yaml" in tracks[
        "tax-personal-income"
    ]["rulespec_destinations"]
    assert all(track["files"] for track in tracks.values())
    assert all(
        track["source_commit"] == manifest["oracle"]["commit"]
        for track in tracks.values()
    )
    assert all(track["rulespec_destinations"] for track in tracks.values())
    assert all(track["canonical_law"] is False for track in tracks.values())


def test_openfisca_fixture_extraction_schema_keeps_oracle_boundary() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)
    schema = manifest["fixture_extraction_schema"]

    assert schema["source_oracle_id"] == "openfisca-aotearoa"
    assert schema["source_commit"] == manifest["oracle"]["commit"]
    assert schema["canonical_law"] is False
    assert schema["authority"] == "comparison_oracle"
    assert schema["allowed_source_kinds"] == [
        "parameter",
        "test",
        "variable_reference",
    ]
    assert schema["required_candidate_fields"] == [
        "fixture_id",
        "source_kind",
        "source_path",
        "source_commit",
        "track_id",
        "rulespec_destination",
        "inputs",
        "expected_outputs",
        "canonical_law",
        "authority",
    ]
    assert schema["promoted_output_boundary"]["standalone_yaml_fixtures_allowed"] is False
    assert schema["promoted_output_boundary"]["allowed_roots"] == [
        "nz/statutes/",
        "nz/regulations/",
        "nz/policies/",
        "data/oracles/fixtures/openfisca-aotearoa/",
    ]
