from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/inventory/nz/social-security-main-benefits.json"
SOURCE_MAP_PATH = ROOT / "data/coverage/tax-benefit-source-map.json"


def _load_json_object(path: Path) -> dict[str, object]:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def _load_json_line(line: str) -> dict[str, object]:
    loaded = cast(object, json.loads(line))
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


def _source_map_track() -> dict[str, object]:
    source_map = _load_json_object(SOURCE_MAP_PATH)
    tracks = _object_list(source_map["tracks"])
    for track in tracks:
        if track["track_id"] == "social-security-main-benefits":
            return track
    raise AssertionError("social-security-main-benefits source-map track missing")


def _citation_paths_from_jsonl(path: Path) -> set[str]:
    records = [_load_json_line(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return {_string_value(record["citation_path"]) for record in records}


def test_social_security_manifest_matches_source_map_batches() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    source_track = _source_map_track()

    assert manifest["track_id"] == "04_social_security_benefits"
    assert manifest["authority"] == "official_source"
    assert manifest["source_map_track_id"] == source_track["track_id"]

    manifest_batches = _object_list(manifest["source_batches"])
    source_batches = _object_list(source_track["first_rule_batches"])

    manifest_by_id = {_string_value(batch["id"]): batch for batch in manifest_batches}
    source_by_id = {_string_value(batch["id"]): batch for batch in source_batches}

    assert set(manifest_by_id) == set(source_by_id)
    for batch_id, manifest_batch in manifest_by_id.items():
        source_batch = source_by_id[batch_id]
        assert manifest_batch["destination"] == source_batch["destination"]
        assert _string_list(manifest_batch["source_requirements"]) == _string_list(
            source_batch["source_requirements"]
        )
        assert _string_list(manifest_batch["oracle_checks"]) == _string_list(
            source_batch["oracle_checks"]
        )


def test_social_security_manifest_points_to_modules_and_provisions() -> None:
    manifest = _load_json_object(MANIFEST_PATH)

    provision_files = _object_list(manifest["provision_files"])
    provision_citations: set[str] = set()
    for provision in provision_files:
        path = ROOT / _string_value(provision["path"])
        assert path.exists()
        declared_paths = set(_string_list(provision["citation_paths"]))
        available_paths = _citation_paths_from_jsonl(path)
        assert declared_paths <= available_paths
        provision_citations.update(declared_paths)

    modules = _object_list(manifest["rulespec_modules"])
    module_paths = {_string_value(module["path"]) for module in modules}
    assert module_paths == {
        "nz/statutes/social_security/main_benefits/entitlement.yaml",
        "nz/statutes/social_security/main_benefits/rates.yaml",
    }

    for module in modules:
        module_path = ROOT / _string_value(module["path"])
        test_path = ROOT / _string_value(module["test_path"])
        citation_paths = set(_string_list(module["corpus_citation_paths"]))
        module_text = module_path.read_text(encoding="utf-8")

        assert module_path.exists()
        assert test_path.exists()
        assert citation_paths <= provision_citations
        for citation_path in citation_paths:
            assert citation_path in module_text

