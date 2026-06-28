from __future__ import annotations

# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import yaml
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "repository-checks.yml"


@pytest.mark.unit
def test_repository_checks_workflow_exposes_validation_and_quality_gates() -> None:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    jobs = workflow["jobs"]

    assert set(jobs) == {"validate", "roadmap-coverage", "quality"}
    assert "uses" in jobs["validate"]
    assert "validate-rulespec.yml" in jobs["validate"]["uses"]

    quality_steps = jobs["quality"]["steps"]
    assert any(step.get("uses") == "prefix-dev/setup-pixi@v0" for step in quality_steps)
    assert any(step.get("run") == "pixi run quality" for step in quality_steps)
