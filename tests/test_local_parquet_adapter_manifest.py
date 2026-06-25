from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/ingestion/local-parquet-layers.json"
FIXTURE_PATH = ROOT / "data/corpus/ingestion/fixtures/local-parquet-reader-smoke.json"
SOURCE_SPINE_PATH = ROOT / "data/corpus/inventory/nz/source-spine.json"
REQUIREMENTS_PATH = ROOT / "conductor/requirements_and_design.md"


def _load_json_object(path: Path) -> dict[str, object]:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


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


def _string_map(value: object) -> dict[str, str]:
    assert isinstance(value, dict)
    raw = cast(dict[object, object], value)
    for key, item in raw.items():
        assert isinstance(key, str)
        assert isinstance(item, str)
    return cast(dict[str, str], raw)


def _source_spine_ids() -> set[str]:
    source_spine = _load_json_object(SOURCE_SPINE_PATH)
    return {
        _string_value(source["id"]) for source in _object_list(source_spine["sources"])
    }


def test_local_parquet_adapter_manifest_covers_track7_requirements() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert manifest["track_id"] == "07_corpus_parquet_ingest"
    assert manifest["adapter_id"] == "local-parquet-layers"
    assert manifest["authority"] == "adapter_contract"
    assert manifest["mode"] == "read_only_local_files"
    assert "corpus-legislation-nz" in requirements
    assert "corpus-nz-hansard" in requirements

    source_ids = {
        _string_value(source["id"]) for source in _object_list(manifest["sources"])
    }
    assert source_ids == {"corpus-legislation-nz", "corpus-nz-hansard"}

    for source in _object_list(manifest["sources"]):
        assert source["status"] == "expected_local_external"
        assert source["payload_format"] == "parquet"
        assert _string_value(source["local_path_env"]).startswith("RULESPEC_NZ_")


def test_local_parquet_adapter_keeps_official_source_boundary() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    source_spine_ids = _source_spine_ids()

    sources = {
        _string_value(source["id"]): source
        for source in _object_list(manifest["sources"])
    }
    legislation = sources["corpus-legislation-nz"]
    hansard = sources["corpus-nz-hansard"]

    assert legislation["canonical_source_id"] == "nz-legislation"
    assert legislation["canonical_source_id"] in source_spine_ids
    assert legislation["legal_authority"] == "official_legislation"
    assert hansard["canonical_source_id"] == "nz-parliament-hansard"
    assert hansard["legal_authority"] == "parliamentary_context"
    assert hansard["used_for_rule_authority"] is False


def test_local_parquet_adapter_table_contracts_support_corpus_joins() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    tables = {
        _string_value(table["id"]): table for table in _object_list(manifest["tables"])
    }

    assert set(tables) == {"legislation_provisions", "hansard_speeches"}

    legislation_columns = set(
        _string_list(tables["legislation_provisions"]["required_columns"])
    )
    assert {
        "citation_path",
        "work_id",
        "document_class",
        "expression_date",
        "text",
        "source_path",
    } <= legislation_columns
    assert tables["legislation_provisions"]["primary_join_key"] == "citation_path"

    hansard_columns = set(_string_list(tables["hansard_speeches"]["required_columns"]))
    assert {
        "sitting_date",
        "chamber",
        "speaker_name",
        "debate_title",
        "text",
        "source_path",
    } <= hansard_columns
    assert tables["hansard_speeches"]["primary_join_key"] == "source_path"

    outputs = _string_map(manifest["normalized_output_paths"])
    assert (
        outputs["legislation_provisions"]
        == "data/corpus/provisions/nz/<document_class>/<run-id>.jsonl"
    )
    assert (
        outputs["legislation_inventory"]
        == "data/corpus/inventory/nz/<document_class>/<run-id>.json"
    )
    assert (
        outputs["hansard_context"] == "data/corpus/provisions/nz/hansard/<run-id>.jsonl"
    )


def test_local_parquet_adapter_records_non_commit_boundaries() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    boundaries = manifest["repository_boundaries"]
    assert isinstance(boundaries, dict)
    boundary_items = cast(dict[str, object], boundaries)

    raw_parquet_globs = _string_list(boundary_items["never_commit_globs"])
    assert "**/*.parquet" in raw_parquet_globs
    assert "data/corpus/local/**" in raw_parquet_globs

    allowed_outputs = set(_string_list(boundary_items["allowed_promoted_outputs"]))
    assert {
        "data/corpus/ingestion/*.json",
        "data/corpus/inventory/nz/*.json",
        "data/corpus/provisions/nz/**/*.jsonl",
    } <= allowed_outputs


def test_local_parquet_adapter_reader_smoke_fixtures_cover_table_schemas() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    fixture_refs = _object_list(manifest["reader_smoke_fixtures"])
    assert len(fixture_refs) == 1

    fixture_ref = fixture_refs[0]
    assert fixture_ref["fixture_id"] == "local-parquet-reader-smoke"
    assert fixture_ref["path"] == FIXTURE_PATH.relative_to(ROOT).as_posix()
    assert fixture_ref["payload_format"] == "arrow_schema_json"
    assert fixture_ref["committed_payload_format"] == "json"

    fixture = _load_json_object(FIXTURE_PATH)
    assert fixture["fixture_id"] == fixture_ref["fixture_id"]
    assert fixture["payload_format"] == "arrow_schema_json"
    assert fixture["canonical_law"] is False
    assert fixture["contains_raw_parquet"] is False

    tables = {
        _string_value(table["id"]): table for table in _object_list(manifest["tables"])
    }
    fixture_tables = {
        _string_value(table["table_id"]): table
        for table in _object_list(fixture["tables"])
    }
    assert set(fixture_tables) == set(tables)

    for table_id, table in tables.items():
        fixture_table = fixture_tables[table_id]
        assert fixture_table["source_id"] == table["source_id"]
        assert fixture_table["primary_join_key"] == table["primary_join_key"]
        assert (
            fixture_table["fixture_path"] == FIXTURE_PATH.relative_to(ROOT).as_posix()
        )
        columns = set(_string_list(fixture_table["columns"]))
        required_columns = set(_string_list(table["required_columns"]))
        assert required_columns <= columns

        sample_rows = _object_list(fixture_table["sample_rows"])
        assert len(sample_rows) == 1
        for row in sample_rows:
            assert required_columns <= set(row)


def test_local_parquet_adapter_deferred_work_excludes_completed_smoke_fixture() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    deferred_work = _string_list(manifest["deferred_work"])

    assert not any(
        "synthetic Parquet or Arrow fixtures" in item for item in deferred_work
    )


def test_local_parquet_adapter_records_live_validation_state() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    live_validation = cast(dict[str, object], manifest["live_local_validation"])

    assert live_validation["validated_at"] == "2026-06-22"
    assert live_validation["status"] == "partial_blocked"
    assert _string_list(live_validation["blocking_reasons"]) != []

    sources = {
        _string_value(source["source_id"]): source
        for source in _object_list(live_validation["sources"])
    }
    assert set(sources) == {"corpus-legislation-nz", "corpus-nz-hansard"}

    legislation = sources["corpus-legislation-nz"]
    assert legislation["env_var_set"] is False
    assert legislation["validated"] is False
    assert legislation["candidate_status"] == "adjacent_noncanonical_candidate_found"

    hansard = sources["corpus-nz-hansard"]
    assert hansard["env_var_set"] is False
    assert hansard["validated"] is False
    assert hansard["candidate_status"] == "candidate_export_found"
    assert _string_value(hansard["candidate_path"]).endswith(
        "corpus-nz-hansard/generated/parquet/hansard.parquet"
    )
