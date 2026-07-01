from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "coverage" / "corpus-citation-provenance-qa.json"
INVENTORY_PATH = ROOT / "data" / "corpus" / "inventory" / "nz" / "tax-benefit-pco-locators.json"


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _collect_string_values(value: Any) -> set[str]:
    collected: set[str] = set()
    if isinstance(value, str):
        collected.add(value)
    elif isinstance(value, list):
        for item in value:
            collected |= _collect_string_values(item)
    elif isinstance(value, dict):
        for item in value.values():
            collected |= _collect_string_values(item)
    return collected


def _inventory_citation_paths() -> set[str]:
    inventory = _load_json(INVENTORY_PATH)
    return {
        value
        for value in _collect_string_values(inventory)
        if value.startswith("nz/")
    }


@pytest.mark.unit
def test_provenance_manifest_is_pinned_and_reviewable() -> None:
    manifest = _load_json(MANIFEST_PATH)

    assert manifest["track_id"] == "38_corpus_citation_pinning_and_provenance_qa"
    assert manifest["status"] == "implemented_pending_review"
    assert manifest["scope"] == "provenance_only"
    assert manifest["source_inventory_path"] == "data/corpus/inventory/nz/tax-benefit-pco-locators.json"
    assert manifest["provenance_checks"] == [
        "module_source_verification_matches_manifest",
        "corpus_inventory_contains_every_pinned_path",
        "tracked_paths_remain_narrow_and_reviewable",
    ]
    assert len(manifest["pinned_citation_sets"]) == 5


@pytest.mark.unit
def test_pinned_citations_exist_in_modules_and_inventory() -> None:
    manifest = _load_json(MANIFEST_PATH)
    inventory_paths = _inventory_citation_paths()

    for citation_set in manifest["pinned_citation_sets"]:
        module_path = ROOT / citation_set["module_path"]
        test_path = ROOT / citation_set["test_path"]
        module = _load_yaml(module_path)
        pinned_paths = set(citation_set["corpus_citation_paths"])

        assert module_path.exists(), citation_set["module_path"]
        assert test_path.exists(), citation_set["test_path"]
        assert pinned_paths <= inventory_paths
        assert pinned_paths <= set(
            module["module"]["source_verification"]["corpus_citation_paths"]
        )
