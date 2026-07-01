from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import tomllib
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_pyproject_enables_strict_linting_typing_and_pydantic_v2() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "ALL" in pyproject["tool"]["ruff"]["lint"]["select"]
    assert pyproject["tool"]["basedpyright"]["typeCheckingMode"] == "strict"
    assert "pydantic>=2.12" in pyproject["project"]["dependencies"]


@pytest.mark.unit
def test_pytest_declares_unit_integration_and_e2e_markers() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    markers = "\n".join(pyproject["tool"]["pytest"]["ini_options"]["markers"])

    assert "unit:" in markers
    assert "integration:" in markers
    assert "e2e:" in markers


@pytest.mark.unit
def test_runtime_cli_and_pytest_goblin_are_not_configured_without_need() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = "\n".join(
        [
            *pyproject["project"]["dependencies"],
            *pyproject["project"]["optional-dependencies"]["dev"],
        ],
    )

    assert "typer" not in dependencies
    assert "pytest-goblin" not in dependencies


@pytest.mark.unit
def test_pixi_tasks_cover_quality_and_test_granularity() -> None:
    pixi = tomllib.loads((ROOT / "pixi.toml").read_text(encoding="utf-8"))
    tasks = pixi["tasks"]

    assert {"test-unit", "test-integration", "test-e2e"} <= set(tasks)
    assert tasks["quality"]["depends-on"] == [
        "lint",
        "format-check",
        "typecheck",
        "test",
        "rust-test",
    ]
