from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/corpus/inventory/nz/income-tax-rate-schedule.json"
RULESPEC_PATH = ROOT / "nz/statutes/income_tax/schedule_1/individual_income_tax.yaml"
SOURCE_MAP_PATH = ROOT / "data/coverage/tax-benefit-source-map.json"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        loaded = json.load(handle)
    assert isinstance(loaded, dict)
    return loaded


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    assert isinstance(loaded, dict)
    return loaded


def _stringify_nested_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _stringify_nested_keys(item) for key, item in value.items()}
    return value


def test_income_tax_rate_manifest_matches_rulespec_source_verification() -> None:
    manifest = _load_json(MANIFEST_PATH)
    rulespec = _load_yaml(RULESPEC_PATH)

    source_verification = rulespec["module"]["source_verification"]

    assert manifest["track_id"] == "03_income_tax_rates"
    assert manifest["authority"] == "official_source"
    assert manifest["rulespec_module"] == RULESPEC_PATH.relative_to(ROOT).as_posix()
    assert manifest["corpus_citation_path"] == source_verification["corpus_citation_path"]
    assert manifest["agency_reference_urls"] == source_verification["agency_reference_urls"]
    assert manifest["verified_values"] == _stringify_nested_keys(source_verification["values"])


def test_income_tax_rate_manifest_matches_source_map_first_batch() -> None:
    manifest = _load_json(MANIFEST_PATH)
    source_map = _load_json(SOURCE_MAP_PATH)

    tax_track = next(
        track
        for track in source_map["tracks"]
        if track["track_id"] == "tax-personal-income"
    )
    batch = next(
        item
        for item in tax_track["first_rule_batches"]
        if item["id"] == "income-tax-rate-scale"
    )

    assert manifest["source_map_track_id"] == tax_track["track_id"]
    assert manifest["source_batch_id"] == batch["id"]
    assert manifest["rulespec_module"] == batch["destination"]
    assert manifest["source_requirements"] == batch["source_requirements"]
    assert manifest["oracle_checks"] == batch["oracle_checks"]


