from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/inventory/nz/gst-acc-levies.json"
GST_RULESPEC_PATH = ROOT / "nz/statutes/gst/rate.yaml"
ACC_RULESPEC_PATH = ROOT / "nz/regulations/acc/earners_levy.yaml"
SOURCE_MAP_PATH = ROOT / "data/coverage/tax-benefit-source-map.json"


def _load_json_object(path: Path) -> dict[str, object]:
    loaded = cast("object", json.loads(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast("dict[str, object]", loaded)


def _load_json_line(line: str) -> dict[str, object]:
    loaded = cast("object", json.loads(line))
    assert isinstance(loaded, dict)
    return cast("dict[str, object]", loaded)


def _load_yaml_object(path: Path) -> dict[str, object]:
    loaded = cast("object", yaml.safe_load(path.read_text(encoding="utf-8")))
    assert isinstance(loaded, dict)
    return cast("dict[str, object]", loaded)


def _object_dict(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return cast("dict[str, object]", value)


def _object_list(value: object) -> list[dict[str, object]]:
    assert isinstance(value, list)
    items = cast("list[object]", value)
    for item in items:
        assert isinstance(item, dict)
    return cast("list[dict[str, object]]", items)


def _string_list(value: object) -> list[str]:
    assert isinstance(value, list)
    items = cast("list[object]", value)
    for item in items:
        assert isinstance(item, str)
    return cast("list[str]", items)


def _string_value(value: object) -> str:
    assert isinstance(value, str)
    return value


def _number_value(value: object) -> int | float:
    assert isinstance(value, int | float)
    return value


def _rule_formulas_by_effective_date(path: Path, rule_name: str) -> dict[str, str]:
    rulespec = _load_yaml_object(path)
    rules = _object_list(rulespec["rules"])
    rule = next(rule for rule in rules if rule["name"] == rule_name)
    return {
        _string_value(version["effective_from"]): _string_value(
            version["formula"],
        ).strip()
        for version in _object_list(rule["versions"])
    }


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
    records = [
        _load_json_line(line) for line in path.read_text(encoding="utf-8").splitlines()
    ]
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
            source_batch["source_requirements"],
        )
        assert _string_list(manifest_batch["oracle_checks"]) == _string_list(
            source_batch["oracle_checks"],
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
        module for module in modules if module["path"] == "nz/statutes/gst/rate.yaml"
    )
    gst_citations = set(_string_list(gst_module["available_corpus_citation_paths"]))
    assert gst_citations == {
        "nz/statute/act/public/1985/0141/section/8-DLM82299",
        "nz/statute/act/public/1985/0141/section/10",
        "nz/statute/act/public/1985/0141/section/12",
    }
    assert _string_list(gst_module["unresolved_corpus_citation_paths"]) == []
    assert "nz/statute/act/public/1985/0141/section/10" not in _string_list(
        manifest["known_corpus_gaps"],
    )


def test_gst_acc_oracle_fixtures_match_rulespec_values_without_authority() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    fixture_refs = _object_list(manifest["oracle_fixtures"])
    fixture_refs_by_id = {_string_value(ref["fixture_id"]): ref for ref in fixture_refs}

    assert set(fixture_refs_by_id) == {
        "policyengine-nz-gst-rate-2025",
        "nztaxmicrosim-acc-earners-levy-2025-2027",
    }

    gst_ref = fixture_refs_by_id["policyengine-nz-gst-rate-2025"]
    assert gst_ref["oracle_id"] == "policyengine-nz"
    assert gst_ref["canonical_law"] is False
    gst_fixture = _load_json_object(ROOT / _string_value(gst_ref["path"]))
    assert gst_fixture["oracle_commit"] == gst_ref["commit"]
    assert gst_fixture["canonical_law"] is False
    assert gst_fixture["rulespec_destination"] == "nz/statutes/gst/rate.yaml"
    gst_values = _object_dict(gst_fixture["normalized_values"])
    assert (
        _string_value(gst_values["gst_standard_rate"])
        == _rule_formulas_by_effective_date(
            GST_RULESPEC_PATH,
            "gst_standard_rate",
        )["2010-10-01"]
    )

    acc_ref = fixture_refs_by_id["nztaxmicrosim-acc-earners-levy-2025-2027"]
    assert acc_ref["oracle_id"] == "nztaxmicrosim"
    assert acc_ref["canonical_law"] is False
    acc_fixture = _load_json_object(ROOT / _string_value(acc_ref["path"]))
    assert acc_fixture["oracle_commit"] == acc_ref["commit"]
    assert acc_fixture["canonical_law"] is False
    assert acc_fixture["rulespec_destination"] == "nz/regulations/acc/earners_levy.yaml"

    acc_values = _object_dict(acc_fixture["normalized_values"])
    rates = _object_dict(acc_values["acc_earners_levy_rate_including_gst"])
    caps = _object_dict(acc_values["acc_earners_levy_maximum_earnings"])
    maximum_levies = _object_dict(acc_values["acc_maximum_levy_including_gst"])

    rulespec_rates = _rule_formulas_by_effective_date(
        ACC_RULESPEC_PATH,
        "acc_earners_levy_rate_including_gst",
    )
    rulespec_caps = _rule_formulas_by_effective_date(
        ACC_RULESPEC_PATH,
        "acc_earners_levy_maximum_earnings",
    )
    for effective_from in ("2025-04-01", "2026-04-01", "2027-04-01"):
        assert _string_value(rates[effective_from]) == rulespec_rates[effective_from]
        assert _number_value(caps[effective_from]) == int(rulespec_caps[effective_from])
        expected_maximum = round(
            _number_value(caps[effective_from]) * float(rulespec_rates[effective_from]),
            2,
        )
        assert _number_value(maximum_levies[effective_from]) == expected_maximum
