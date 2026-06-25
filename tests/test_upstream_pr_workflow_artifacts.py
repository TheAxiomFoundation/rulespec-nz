from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = ROOT / "conductor" / "workflows" / "upstream-pr"
AGENT_ROOT = ROOT / ".agents" / "upstream-pr"
SKILL_PATH = ROOT / ".codex" / "skills" / "upstream-pr-workflow" / "SKILL.md"
TRACK_ROOT = ROOT / "conductor" / "tracks" / "archive" / "11_upstream_pr_workflows"
WORKFLOW_MANIFEST = WORKFLOW_ROOT / "workflow.json"


def load_workflow_manifest() -> dict[str, Any]:
    return json.loads(WORKFLOW_MANIFEST.read_text(encoding="utf-8"))


@pytest.mark.unit
def test_upstream_pr_workflow_artifacts_exist() -> None:
    expected = {
        WORKFLOW_MANIFEST,
        WORKFLOW_ROOT / "strategy.md",
        WORKFLOW_ROOT / "change-inventory.md",
        WORKFLOW_ROOT / "slice-selection.md",
        WORKFLOW_ROOT / "upstream-readiness.md",
        WORKFLOW_ROOT / "branch-pr-prep.md",
        WORKFLOW_ROOT / "parallel-review.md",
        AGENT_ROOT / "inventory-agent.md",
        AGENT_ROOT / "provenance-readiness-agent.md",
        AGENT_ROOT / "packaging-agent.md",
        SKILL_PATH,
        TRACK_ROOT / "metadata.json",
        TRACK_ROOT / "spec.md",
        TRACK_ROOT / "plan.md",
    }
    assert [
        p.relative_to(ROOT).as_posix() for p in sorted(expected) if not p.exists()
    ] == []


@pytest.mark.unit
def test_skill_requires_executable_workflow_graph() -> None:
    skill = SKILL_PATH.read_text(encoding="utf-8")
    assert "workflow.json" in skill
    assert "parallel_lanes" in skill
    assert "dependency order and blockers" in skill
    assert "Default to automated completion" in skill
    assert "Do not push or open a PR unless the user explicitly asks" in skill


@pytest.mark.unit
def test_workflow_manifest_declares_dependencies_blockers_and_lanes() -> None:
    manifest = load_workflow_manifest()
    steps = {step["id"]: step for step in manifest["steps"]}
    lanes = {lane["id"]: lane for lane in manifest["parallel_lanes"]}
    classes = {item["id"]: item for item in manifest["slice_classes"]}

    assert manifest["human_input_required"] is False
    assert manifest["live_submission_requires_explicit_user_request"] is True
    assert manifest["default_policy"]["oracle_authority"] == "comparison_only"
    assert (
        manifest["default_policy"]["legal_authority"] == "official_new_zealand_sources"
    )
    assert steps["change-inventory"]["depends_on"] == []
    assert steps["slice-selection"]["depends_on"] == ["change-inventory"]
    assert steps["upstream-readiness"]["depends_on"] == ["slice-selection"]
    assert steps["parallel-review"]["depends_on"] == ["slice-selection"]
    assert steps["branch-pr-prep"]["depends_on"] == [
        "upstream-readiness",
        "parallel-review",
    ]
    assert set(lanes) == {"inventory", "readiness", "packaging"}
    assert set(classes) == {"legal-content", "adapter", "tooling", "docs", "generated"}

    for step in steps.values():
        assert step["blockers"], step["id"]
        assert step["outputs"], step["id"]
        assert (ROOT / step["path"]).exists(), step["path"]

    for lane in lanes.values():
        assert (ROOT / lane["agent_spec"]).exists(), lane["agent_spec"]
        assert set(lane["forbidden_actions"]) >= {"push", "open-pr"}
        assert "report" in lane["allowed_actions"]

    assert "official-provenance" in classes["legal-content"]["requires"]
    assert "companion-tests" in classes["legal-content"]["requires"]
    assert "reproducibility-note" in classes["generated"]["requires"]


@pytest.mark.unit
def test_archived_track_11_metadata_records_closeout() -> None:
    metadata = json.loads((TRACK_ROOT / "metadata.json").read_text(encoding="utf-8"))
    automation = metadata["automation"]
    assert metadata["status"] == "archived_after_review_remediation"
    assert metadata["implementation_complete"] is True
    assert metadata["review_complete"] is True
    assert metadata["review_required"] is False
    assert metadata["blockers"] == []
    assert automation["human_input_required"] is False
    assert automation["manifest"] == "conductor/workflows/upstream-pr/workflow.json"
    assert set(automation["parallelization"]) == {"inventory", "readiness", "packaging"}


@pytest.mark.unit
def test_track_11_is_removed_from_active_index() -> None:
    tracks = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    active, archived = tracks.split("## Archived Tracks", maxsplit=1)
    assert "Track 11" not in active
    assert "conductor/tracks/archive/11_upstream_pr_workflows" in archived
