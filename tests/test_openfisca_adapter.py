from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

from pathlib import Path

import pytest

from rulespec_nz.openfisca_adapter import (
    build_openfisca_fixture_candidates,
    build_openfisca_reference_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.integration
def test_openfisca_manifest_uses_pinned_oracle_commit_and_is_not_authority() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)

    assert manifest["oracle"]["id"] == "openfisca-aotearoa"
    assert manifest["oracle"]["commit"] == "c36c40bcf553dc95ddca473be12440d4be9d0560"
    assert manifest["canonical_law"] is False
    assert manifest["authority"] == "comparison_oracle"


@pytest.mark.integration
def test_openfisca_manifest_groups_track_references_with_files() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)
    tracks = {track["track_id"]: track for track in manifest["tracks"]}

    assert "tax-personal-income" in tracks
    assert (
        "openfisca_aotearoa/variables/acts/income_tax/individual.py"
        in tracks["tax-personal-income"]["files"]
    )
    assert (
        tracks["tax-personal-income"]["source_commit"] == manifest["oracle"]["commit"]
    )
    assert (
        "nz/statutes/income_tax/core/taxable_income.yaml"
        in tracks["tax-personal-income"]["rulespec_destinations"]
    )
    assert all(track["files"] for track in tracks.values())
    assert all(
        track["source_commit"] == manifest["oracle"]["commit"]
        for track in tracks.values()
    )
    assert all(track["rulespec_destinations"] for track in tracks.values())
    assert all(track["canonical_law"] is False for track in tracks.values())


@pytest.mark.integration
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
    assert (
        schema["promoted_output_boundary"]["standalone_yaml_fixtures_allowed"] is False
    )
    assert schema["promoted_output_boundary"]["allowed_roots"] == [
        "nz/statutes/",
        "nz/regulations/",
        "nz/policies/",
        "data/oracles/fixtures/openfisca-aotearoa/",
    ]


@pytest.mark.e2e
def test_openfisca_fixture_dry_run_normalizes_selected_snippets() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)
    candidates = build_openfisca_fixture_candidates(
        manifest,
        [
            {
                "source_kind": "parameter",
                "source_path": (
                    "openfisca_aotearoa/parameters/taxes/income_tax/"
                    "individual_income_tax_rate.yaml"
                ),
                "track_id": "tax-personal-income",
                "value": 0.105,
            },
            {
                "source_kind": "test",
                "source_path": "openfisca_aotearoa/tests/social_security/super.yaml",
                "track_id": "superannuation",
                "inputs": {"age": 65},
                "expected_outputs": {"eligible": True},
            },
        ],
    )

    parameter_candidate, test_candidate = candidates

    assert parameter_candidate["fixture_id"] == (
        "openfisca-aotearoa:tax-personal-income:parameter:individual_income_tax_rate"
    )
    assert parameter_candidate["source_commit"] == manifest["oracle"]["commit"]
    assert parameter_candidate["rulespec_destination"] == (
        "nz/statutes/income_tax/schedule_1/individual_income_tax.yaml"
    )
    assert parameter_candidate["inputs"] == {}
    assert parameter_candidate["expected_outputs"] == {"value": 0.105}
    assert parameter_candidate["canonical_law"] is False
    assert parameter_candidate["authority"] == "comparison_oracle"

    assert test_candidate["fixture_id"] == (
        "openfisca-aotearoa:superannuation:test:super"
    )
    assert test_candidate["rulespec_destination"] == (
        "nz/statutes/superannuation/nz_superannuation.yaml"
    )
    assert test_candidate["inputs"] == {"age": 65}
    assert test_candidate["expected_outputs"] == {"eligible": True}
    assert all(candidate["canonical_law"] is False for candidate in candidates)


@pytest.mark.unit
def test_openfisca_fixture_dry_run_rejects_unexpected_snippet_fields() -> None:
    manifest = build_openfisca_reference_manifest(ROOT)

    with pytest.raises(ValueError, match="Invalid OpenFisca snippet") as exc_info:
        build_openfisca_fixture_candidates(
            manifest,
            [
                {
                    "source_kind": "parameter",
                    "source_path": (
                        "openfisca_aotearoa/parameters/taxes/income_tax/"
                        "individual_income_tax_rate.yaml"
                    ),
                    "track_id": "tax-personal-income",
                    "value": 0.105,
                    "canonical_law": True,
                },
            ],
        )

    cause = exc_info.value.__cause__
    assert cause is not None
    assert "extra_forbidden" in str(cause)
