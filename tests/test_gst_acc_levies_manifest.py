from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/inventory/nz/gst-acc-levies.json"
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


def _source_map_tracks() -> dict[str, dict[str, object]]:
    source_map = _load_json_object(SOURCE_MAP_PATH)
    tracks = _object_list(source_map["tracks"])
    wanted = {"levies-acc", "consumption-and-indirect-tax"}
    return {
        _string_value(track["track_id"]): track
        for track in tracks
        if track["track_id"] in wanted
    }


def _citation_paths_from_jsonl(path: Path) -> set[str]:
    records = [_load_json_line(line) for line in path.read_text(encoding="utf-8").splitlines()]
    return {_string_value(record["citation_path"]) for record in records}


def test_gst_acc_manifest_matches_source_map_batches() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    source_tracks = _source_map_tracks()

    assert manifest["track_id"] == "05_gst_acc_levies"
    assert manifest["authority"] == "official_source"
    assert set(_string_list(manifest["source_map_track_ids"])) == set(source_tracks)

    manifest_batches = _object_list(manifest["source_batches"])
    manifest_by_id = {_string_value(batch["id"]): batch for batch in manifest_batches}

    expected_batches: dict[str, dict[str, object]] = {}
    for source_track in source_tracks.values():
        for batch in _object_list(source_track["first_rule_batches"]):
            expected_batches[_string_value(batch["id"])] = batch

    assert set(manifest_by_id) == set(expected_batches)
    for batch_id, manifest_batch in manifest_by_id.items():
        source_batch = expected_batches[batch_id]
        assert manifest_batch["destination"] == source_batch["destination"]
        assert _string_list(manifest_batch["source_requirements"]) == _string_list(
            source_batch["source_requirements"]
        )
        assert _string_list(manifest_batch["oracle_checks"]) == _string_list(
            source_batch["oracle_checks"]
        )


def test_gst_acc_manifest_points_to_modules_provisions_and_known_gaps() -> None:
    manifest = _load_json_object(MANIFEST_PATH)

    provision_citations: set[str] = set()
    for provision in _object_list(manifest["provision_files"]):
        path = ROOT / _string_value(provision["path"])
        assert path.exists()
        declared_paths = set(_string_list(provision["citation_paths"]))
        available_paths = _citation_paths_from_jsonl(path)
        assert declared_paths <= available_paths
        provision_citations.update(declared_paths)

    expected_modules = {
        "nz/statutes/gst/rate.yaml",
        "nz/regulations/acc/earners_levy.yaml",
    }
    modules = _object_list(manifest["rulespec_modules"])
    assert {_string_value(module["path"]) for module in modules} == expected_modules

    for module in modules:
        module_path = ROOT / _string_value(module["path"])
        test_path = ROOT / _string_value(module["test_path"])
        module_text = module_path.read_text(encoding="utf-8")
        available = set(_string_list(module["available_corpus_citation_paths"]))
        unresolved = set(_string_list(module["unresolved_corpus_citation_paths"]))
        agency_citations = set(_string_list(module["agency_citation_paths"]))

        assert module_path.exists()
        assert test_path.exists()
        assert available <= provision_citations
        assert unresolved.isdisjoint(provision_citations)
        for citation_path in available | unresolved | agency_citations:
            assert citation_path in module_text

    gst_module = next(
        module
        for module in modules
        if module["path"] == "nz/statutes/gst/rate.yaml"
    )
    gst_citations = set(_string_list(gst_module["available_corpus_citation_paths"]))
    assert gst_citations == {
        "nz/statute/act/public/1985/0141/section/8-DLM82299",
        "nz/statute/act/public/1985/0141/section/10",
        "nz/statute/act/public/1985/0141/section/12",
    }
    assert _string_list(gst_module["unresolved_corpus_citation_paths"]) == []
    assert "nz/statute/act/public/1985/0141/section/10" not in _string_list(
        manifest["known_corpus_gaps"]
    )
