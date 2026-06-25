from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/inventory/nz/new-zealand-superannuation.json"
CORE_RULESPEC_PATH = ROOT / "nz/statutes/new_zealand_superannuation/core.yaml"
SOURCE_MAP_PATH = ROOT / "data/coverage/tax-benefit-source-map.json"


def _load_json_object(path: Path) -> dict[str, object]:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def _load_json_line(line: str) -> dict[str, object]:
    loaded = cast(object, json.loads(line))
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


def _number_value(value: object) -> int | float:
    assert isinstance(value, int | float)
    return value


def _rule_formula(path: Path, rule_name: str) -> str:
    rulespec = _load_yaml_object(path)
    rules = _object_list(rulespec["rules"])
    rule = next(rule for rule in rules if rule["name"] == rule_name)
    versions = _object_list(rule["versions"])
    return _string_value(versions[0]["formula"]).strip()


def _source_map_track() -> dict[str, object]:
    source_map = _load_json_object(SOURCE_MAP_PATH)
    tracks = _object_list(source_map["tracks"])
    for track in tracks:
        if track["track_id"] == "superannuation":
            return track
    raise AssertionError("superannuation source-map track missing")


def _citation_paths_from_jsonl(path: Path) -> set[str]:
    records = [
        _load_json_line(line) for line in path.read_text(encoding="utf-8").splitlines()
    ]
    return {_string_value(record["citation_path"]) for record in records}


def test_nz_superannuation_manifest_matches_source_map_batch() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    source_track = _source_map_track()

    assert manifest["track_id"] == "06_nz_superannuation"
    assert manifest["authority"] == "official_source"
    assert manifest["source_map_track_id"] == source_track["track_id"]
    assert (
        manifest["canonical_source_map_destination"]
        == "nz/statutes/superannuation/nz_superannuation.yaml"
    )

    manifest_batches = _object_list(manifest["source_batches"])
    source_batches = _object_list(source_track["first_rule_batches"])

    manifest_by_id = {_string_value(batch["id"]): batch for batch in manifest_batches}
    source_by_id = {_string_value(batch["id"]): batch for batch in source_batches}

    assert set(manifest_by_id) == {"nz-superannuation"}
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


def test_nz_superannuation_manifest_points_to_modules_and_provisions() -> None:
    manifest = _load_json_object(MANIFEST_PATH)

    provision_citations: set[str] = set()
    for provision in _object_list(manifest["provision_files"]):
        path = ROOT / _string_value(provision["path"])
        assert path.exists()
        declared_paths = set(_string_list(provision["citation_paths"]))
        available_paths = _citation_paths_from_jsonl(path)
        assert declared_paths <= available_paths
        provision_citations.update(declared_paths)

    modules = _object_list(manifest["rulespec_modules"])
    module_paths = {_string_value(module["path"]) for module in modules}
    assert module_paths == {
        "nz/statutes/new_zealand_superannuation/core.yaml",
        "nz/statutes/new_zealand_superannuation/special_rates.yaml",
    }

    for module in modules:
        module_path = ROOT / _string_value(module["path"])
        test_path = ROOT / _string_value(module["test_path"])
        citation_paths = set(_string_list(module["available_corpus_citation_paths"]))
        module_text = module_path.read_text(encoding="utf-8")

        assert module_path.exists()
        assert test_path.exists()
        assert citation_paths <= provision_citations
        for citation_path in citation_paths:
            assert citation_path in module_text


def test_nz_superannuation_manifest_records_path_divergence() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    divergences = _object_list(manifest["known_path_divergences"])

    assert len(divergences) == 1
    divergence = divergences[0]
    assert (
        divergence["source_map_destination"]
        == "nz/statutes/superannuation/nz_superannuation.yaml"
    )
    assert set(_string_list(divergence["implemented_modules"])) == {
        "nz/statutes/new_zealand_superannuation/core.yaml",
        "nz/statutes/new_zealand_superannuation/special_rates.yaml",
    }


def test_nz_superannuation_manifest_records_destination_reconciliation_decision() -> (
    None
):
    manifest = _load_json_object(MANIFEST_PATH)
    reconciliation = cast(dict[str, object], manifest["destination_reconciliation"])

    assert reconciliation["decision"] == "keep_split_modules"
    assert reconciliation["compatibility_wrapper_added"] is False
    assert (
        reconciliation["canonical_source_map_destination"]
        == "nz/statutes/superannuation/nz_superannuation.yaml"
    )
    assert set(_string_list(reconciliation["implemented_modules"])) == {
        "nz/statutes/new_zealand_superannuation/core.yaml",
        "nz/statutes/new_zealand_superannuation/special_rates.yaml",
    }
    assert _string_value(reconciliation["reason"]) != ""


def test_nz_superannuation_oracle_fixture_matches_age_threshold_without_authority() -> (
    None
):
    manifest = _load_json_object(MANIFEST_PATH)
    fixture_refs = _object_list(manifest["oracle_fixtures"])
    assert len(fixture_refs) == 1

    fixture_ref = fixture_refs[0]
    assert fixture_ref["oracle_id"] == "openfisca-aotearoa"
    assert fixture_ref["canonical_law"] is False

    fixture = _load_json_object(ROOT / _string_value(fixture_ref["path"]))
    assert fixture["oracle_id"] == fixture_ref["oracle_id"]
    assert fixture["oracle_commit"] == fixture_ref["commit"]
    assert fixture["canonical_law"] is False
    assert (
        fixture["rulespec_destination"]
        == "nz/statutes/new_zealand_superannuation/core.yaml"
    )

    normalized = _object_dict(fixture["normalized_values"])
    assert _number_value(normalized["nz_super_age_threshold"]) == int(
        _rule_formula(CORE_RULESPEC_PATH, "nz_super_age_threshold")
    )

    scenarios = _object_list(fixture["scenario_outputs"])
    assert len(scenarios) == 9
    assert {scenario["super_entitled"] for scenario in scenarios} == {False, True}
    assert {scenario["super_eligibility_age"] for scenario in scenarios} == {0, 65}

    assert fixture["rate_fixture_status"] == "not_available_in_pinned_oracle"
    assert _string_value(fixture["rate_fixture_blocker"]) != ""
