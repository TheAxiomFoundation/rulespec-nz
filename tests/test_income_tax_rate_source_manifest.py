from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/inventory/nz/income-tax-rate-schedule.json"
RULESPEC_PATH = ROOT / "nz/statutes/income_tax/schedule_1/individual_income_tax.yaml"
SOURCE_MAP_PATH = ROOT / "data/coverage/tax-benefit-source-map.json"


def _load_json_object(path: Path) -> dict[str, object]:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def _load_yaml_object(path: Path) -> dict[str, object]:
    loaded = cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def _object_dict(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return cast(dict[str, object], value)


def _object_list(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    items = cast(list[object], value)
    for item in items:
        assert isinstance(item, dict)
    return cast(list[dict[str, object]], items)


def _string_list(value: object) -> list[str]:
    assert isinstance(value, list)
    items = cast(list[object], value)
    for item in items:
        assert isinstance(item, str)
    return cast(list[str], items)


def _string_value(value: object) -> str:
    assert isinstance(value, str)
    return value


def _stringify_nested_keys(value: object) -> object:
    if isinstance(value, dict):
        items = cast(dict[object, object], value)
        return {str(key): _stringify_nested_keys(item) for key, item in items.items()}
    return value


def test_income_tax_rate_manifest_matches_rulespec_source_verification() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    rulespec = _load_yaml_object(RULESPEC_PATH)

    source_verification = _object_dict(
        _object_dict(rulespec["module"])["source_verification"]
    )

    assert manifest["track_id"] == "03_income_tax_rates"
    assert manifest["authority"] == "official_source"
    assert manifest["rulespec_module"] == RULESPEC_PATH.relative_to(ROOT).as_posix()
    assert (
        manifest["corpus_citation_path"] == source_verification["corpus_citation_path"]
    )
    assert (
        manifest["agency_reference_urls"]
        == source_verification["agency_reference_urls"]
    )
    assert manifest["verified_values"] == _stringify_nested_keys(
        source_verification["values"]
    )


def test_income_tax_rate_manifest_matches_source_map_first_batch() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    source_map = _load_json_object(SOURCE_MAP_PATH)

    tax_track = next(
        track
        for track in _object_list(source_map["tracks"])
        if track["track_id"] == "tax-personal-income"
    )
    batch = next(
        item
        for item in _object_list(tax_track["first_rule_batches"])
        if item["id"] == "income-tax-rate-scale"
    )

    assert manifest["source_map_track_id"] == tax_track["track_id"]
    assert manifest["source_batch_id"] == batch["id"]
    assert manifest["rulespec_module"] == batch["destination"]
    assert manifest["source_requirements"] == batch["source_requirements"]
    assert manifest["oracle_checks"] == batch["oracle_checks"]


def test_income_tax_rate_manifest_points_to_schedule_1_provision_extract() -> None:
    manifest = _load_json_object(MANIFEST_PATH)

    provision_files = _object_list(manifest["provision_files"])
    assert len(provision_files) == 1

    provision_file = provision_files[0]
    provision_path = ROOT / _string_value(provision_file["path"])
    assert provision_path.exists()

    declared_paths = set(_string_list(provision_file["citation_paths"]))
    assert declared_paths == {manifest["corpus_citation_path"]}

    provision_records = [
        _load_json_object_line(line)
        for line in provision_path.read_text(encoding="utf-8").splitlines()
    ]
    available_paths = {
        _string_value(record["citation_path"]) for record in provision_records
    }
    assert declared_paths <= available_paths


def test_income_tax_rate_oracle_fixture_matches_rulespec_values_without_authority() -> (
    None
):
    manifest = _load_json_object(MANIFEST_PATH)
    oracle_fixtures = _object_list(manifest["oracle_fixtures"])
    assert len(oracle_fixtures) == 1

    fixture_ref = oracle_fixtures[0]
    assert fixture_ref["oracle_id"] == "nztaxmicrosim"
    assert fixture_ref["canonical_law"] is False

    fixture = _load_json_object(ROOT / _string_value(fixture_ref["path"]))
    assert fixture["oracle_id"] == fixture_ref["oracle_id"]
    assert fixture["oracle_commit"] == fixture_ref["commit"]
    assert fixture["canonical_law"] is False
    assert fixture["rulespec_destination"] == manifest["rulespec_module"]
    assert fixture["normalized_values"] == manifest["verified_values"]


def _load_json_object_line(line: str) -> dict[str, object]:
    loaded = cast(object, json.loads(line))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def test_legacy_tax_rate_ingest_track_is_archived_as_track3_context() -> None:
    track3 = _load_json_object(
        ROOT / "conductor/tracks/archive/03_income_tax_rates/metadata.json"
    )
    legacy = _load_json_object(
        ROOT / "conductor/tracks/archive/nz_ingest_tax_rate_20260619/metadata.json"
    )
    tracks_index = (ROOT / "conductor/tracks.md").read_text(encoding="utf-8")

    assert legacy["track_id"] == "nz_ingest_tax_rate_20260619"
    assert legacy["status"] == "archived_superseded"
    assert legacy["superseded_by_track_id"] == track3["track_id"]
    assert (
        legacy["superseded_by_track_path"]
        == "conductor/tracks/archive/03_income_tax_rates/"
    )
    superseded_ids = _string_list(track3["supersedes_track_ids"])
    superseded_paths = _string_list(track3["superseded_track_paths"])

    assert "nz_ingest_tax_rate_20260619" in superseded_ids
    assert "conductor/tracks/archive/nz_ingest_tax_rate_20260619/" in superseded_paths
    assert not (ROOT / "conductor/tracks/nz_ingest_tax_rate_20260619").exists()
    assert "conductor/tracks/archive/nz_ingest_tax_rate_20260619/" in tracks_index
