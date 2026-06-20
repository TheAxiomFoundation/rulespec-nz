from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/ingestion/local-parquet-layers.json"
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
    return {_string_value(source["id"]) for source in _object_list(source_spine["sources"])}


def test_local_parquet_adapter_manifest_covers_track7_requirements() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert manifest["track_id"] == "07_corpus_parquet_ingest"
    assert manifest["adapter_id"] == "local-parquet-layers"
    assert manifest["authority"] == "adapter_contract"
    assert manifest["mode"] == "read_only_local_files"
    assert "corpus-legislation-nz" in requirements
    assert "corpus-nz-hansard" in requirements

    source_ids = {_string_value(source["id"]) for source in _object_list(manifest["sources"])}
    assert source_ids == {"corpus-legislation-nz", "corpus-nz-hansard"}

    for source in _object_list(manifest["sources"]):
        assert source["status"] == "expected_local_external"
        assert source["payload_format"] == "parquet"
        assert _string_value(source["local_path_env"]).startswith("RULESPEC_NZ_")


def test_local_parquet_adapter_keeps_official_source_boundary() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    source_spine_ids = _source_spine_ids()

    sources = {
        _string_value(source["id"]): source for source in _object_list(manifest["sources"])
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

    legislation_columns = set(_string_list(tables["legislation_provisions"]["required_columns"]))
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
    assert outputs["legislation_provisions"] == "data/corpus/provisions/nz/<document_class>/<run-id>.jsonl"
    assert outputs["legislation_inventory"] == "data/corpus/inventory/nz/<document_class>/<run-id>.json"
    assert outputs["hansard_context"] == "data/corpus/provisions/nz/hansard/<run-id>.jsonl"


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

