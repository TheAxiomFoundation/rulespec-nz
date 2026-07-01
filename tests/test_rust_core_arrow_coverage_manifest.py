from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict, cast


ROOT = Path(__file__).resolve().parents[1]


class CoverageLayer(TypedDict):
    """Coverage status for a single runtime layer."""

    coverage_command: str
    status: str
    threshold_met: bool
    blocker: str


class CoverageEvidence(TypedDict):
    """Top-level coverage evidence record for the Rust core track."""

    track_id: str
    coverage_threshold_percent: int
    layers: dict[str, CoverageLayer]
    supporting_gates: list[str]


def test_track1_coverage_evidence_records_threshold_status_and_blockers() -> None:
    evidence_path = ROOT / "data/coverage/rust-core-arrow-coverage.json"
    evidence = cast(
        "CoverageEvidence",
        json.loads(evidence_path.read_text(encoding="utf-8")),
    )

    assert evidence["track_id"] == "01_rust_core_arrow"
    assert evidence["coverage_threshold_percent"] == 90

    layers = evidence["layers"]
    native = layers["native_rust"]
    assert native["coverage_command"] == (
        "cargo llvm-cov --no-default-features --summary-only --json"
    )
    assert native["status"] == "blocked"
    assert native["threshold_met"] is False
    assert "profiler_builtins" in native["blocker"]

    python = layers["python_binding"]
    assert (
        python["coverage_command"]
        == "cargo test --no-default-features --features python"
    )
    assert python["status"] == "blocked"
    assert python["threshold_met"] is False
    assert python["blocker"]  # non-empty blocker string

    support = evidence["supporting_gates"]
    assert "cargo test --no-default-features" in support
    assert "cargo check --no-default-features --features python" in support
    assert "python -m pytest tests -p no:cacheprovider" in support
