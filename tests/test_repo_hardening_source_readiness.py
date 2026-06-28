from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, cast

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "coverage" / "repo-hardening-source-readiness.json"


def load_json(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8-sig")))


@pytest.mark.unit
def test_repo_hardening_manifest_has_track_metadata() -> None:
    manifest = load_json(MANIFEST_PATH)

    assert manifest["track_id"] == "19_repo_hardening_and_source_readiness"
    assert manifest["jurisdiction"] == "nz"
    assert manifest["status"] == "reviewed_ready"


@pytest.mark.unit
def test_required_quality_tasks_are_configured() -> None:
    manifest = load_json(MANIFEST_PATH)
    pixi = tomllib.loads((ROOT / "pixi.toml").read_text(encoding="utf-8"))

    assert set(manifest["quality_gates"]["required_pixi_tasks"]) <= set(pixi["tasks"])
    assert pixi["tasks"]["quality"]["depends-on"] == [
        "lint",
        "format-check",
        "typecheck",
        "test",
        "rust-test",
    ]


@pytest.mark.unit
def test_ci_readiness_records_live_workflow_checks() -> None:
    manifest = load_json(MANIFEST_PATH)
    workflow_path = ROOT / manifest["ci_readiness"]["workflow"]
    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))

    jobs = workflow["jobs"]
    assert jobs["validate"]["uses"] == manifest["ci_readiness"][
        "reusable_validation_workflow"
    ]
    assert (
        jobs["roadmap-coverage"]["steps"][1]["run"]
        == manifest["ci_readiness"]["roadmap_check_command"]
    )


@pytest.mark.unit
def test_source_readiness_matches_source_map_and_backlog() -> None:
    manifest = load_json(MANIFEST_PATH)
    source_map = load_json(ROOT / manifest["source_readiness"]["source_map"])
    backlog = load_json(ROOT / manifest["source_readiness"]["backlog"])

    assert source_map["current_blockers"] == manifest["source_readiness"][
        "current_blockers_expected"
    ]

    source_map_track_ids = {track["track_id"] for track in source_map["tracks"]}
    backlog_track_ids = {track["id"] for track in backlog["tracks"]}
    assert source_map_track_ids <= backlog_track_ids


@pytest.mark.unit
def test_pco_locator_readiness_is_recorded() -> None:
    manifest = load_json(MANIFEST_PATH)
    source_map = load_json(ROOT / manifest["source_readiness"]["source_map"])

    expected = manifest["source_readiness"]["pco_corpus_locator"]
    actual = source_map["pco_corpus_locator"]

    assert actual["run_id"] == expected["run_id"]
    assert actual["path"] == expected["path"]
    assert actual["axiom_corpus_ref"] == expected["axiom_corpus_ref"]
    assert actual["source_file_count"] >= expected["minimum_source_files"]
    assert actual["provisions_written"] >= expected["minimum_provisions"]


@pytest.mark.unit
def test_agency_inventory_statuses_are_explicit() -> None:
    manifest = load_json(MANIFEST_PATH)
    source_map = load_json(ROOT / manifest["source_readiness"]["source_map"])

    allowed = set(manifest["source_readiness"]["required_source_statuses"])
    statuses = {
        source["status"]
        for track in source_map["tracks"]
        for source in track["official_source_refs"]
    }

    assert statuses <= allowed
    assert set(manifest["source_readiness"]["agency_inventory_statuses"]) <= statuses
