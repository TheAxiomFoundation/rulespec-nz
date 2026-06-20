from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/analysis/regression-voi-pipeline.json"
ORACLE_INDEX_PATH = ROOT / "data/oracles/oracle-index.json"
REQUIREMENTS_PATH = ROOT / "conductor/requirements_and_design.md"
MICROSIM_PATH = ROOT / "data/microsimulation/synthetic-population-builder.json"


def _load_json_object(path: Path) -> dict[str, object]:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
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


def _string_map(value: object) -> dict[str, str]:
    assert isinstance(value, dict)
    raw = cast(dict[object, object], value)
    for key, item in raw.items():
        assert isinstance(key, str)
        assert isinstance(item, str)
    return cast(dict[str, str], raw)


def _oracle_ids() -> set[str]:
    oracle_index = _load_json_object(ORACLE_INDEX_PATH)
    return {_string_value(oracle["id"]) for oracle in _object_list(oracle_index["oracles"])}


def test_regression_voi_manifest_covers_track9_requirements() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert manifest["track_id"] == "09_regression_voi_pipeline"
    assert manifest["pipeline_id"] == "regression-voi-pipeline"
    assert manifest["authority"] == "adapter_contract"
    assert manifest["mode"] == "read_only_external_analysis_tools"
    assert "mars" in requirements
    assert "voiage" in requirements

    tool_ids = {_string_value(tool["id"]) for tool in _object_list(manifest["tools"])}
    assert tool_ids == {"mars", "voiage"}


def test_regression_voi_manifest_keeps_tool_registry_status_explicit() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    oracle_ids = _oracle_ids()
    tools = {_string_value(tool["id"]): tool for tool in _object_list(manifest["tools"])}

    assert tools["voiage"]["oracle_id"] == "voiage"
    assert tools["voiage"]["oracle_id"] in oracle_ids
    assert tools["voiage"]["status"] == "pinned_research_oracle"

    assert tools["mars"]["oracle_id"] is None
    assert tools["mars"]["status"] == "expected_local_external"
    assert tools["mars"]["registry_gap"] == "not_pinned_in_oracle_index"


def test_regression_voi_manifest_inputs_align_with_microsimulation_contract() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    microsim = _load_json_object(MICROSIM_PATH)

    expected_entity_tables = {
        _string_value(table["id"]) for table in _object_list(microsim["entity_tables"])
    }
    inputs = {_string_value(item["id"]): item for item in _object_list(manifest["inputs"])}

    assert set(inputs) == {"simulation_outputs", "population_weights", "scenario_metadata"}
    assert inputs["simulation_outputs"]["source_manifest"] == str(MICROSIM_PATH.relative_to(ROOT)).replace("\\", "/")
    assert set(_string_list(inputs["simulation_outputs"]["required_entity_tables"])) <= expected_entity_tables
    assert inputs["population_weights"]["required_column"] == "household_weight"
    assert inputs["scenario_metadata"]["required_key"] == "run_id"


def test_regression_voi_manifest_output_contract_is_stable() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    outputs = {_string_value(item["id"]): item for item in _object_list(manifest["outputs"])}

    assert set(outputs) == {"regression_dataset", "voi_decision_table", "summary_report"}

    regression_columns = set(_string_list(outputs["regression_dataset"]["required_columns"]))
    assert {
        "run_id",
        "scenario_id",
        "person_id",
        "household_weight",
        "net_income_delta",
        "emtr_delta",
    } <= regression_columns
    assert outputs["regression_dataset"]["format"] == "jsonl"

    voi_columns = set(_string_list(outputs["voi_decision_table"]["required_columns"]))
    assert {"decision_id", "expected_value", "expected_value_of_information"} <= voi_columns
    assert outputs["summary_report"]["format"] == "markdown"


def test_regression_voi_manifest_records_metrics_and_boundaries() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    metrics = {_string_value(metric["id"]): metric for metric in _object_list(manifest["metrics"])}
    boundaries = manifest["repository_boundaries"]
    assert isinstance(boundaries, dict)
    boundary_items = cast(dict[str, object], boundaries)

    assert set(metrics) == {"net_income_delta", "emtr_delta", "voi_evpi"}
    assert metrics["net_income_delta"]["unit"] == "NZD"
    assert metrics["emtr_delta"]["unit"] == "rate"
    assert metrics["voi_evpi"]["unit"] == "NZD"

    never_commit = set(_string_list(boundary_items["never_commit_globs"]))
    assert "data/analysis/local/**" in never_commit
    assert "data/analysis/raw/**" in never_commit
    assert "**/*.parquet" in never_commit

    promoted_outputs = set(_string_list(boundary_items["allowed_promoted_outputs"]))
    assert "data/analysis/*.json" in promoted_outputs
    assert "data/analysis/fixtures/*.jsonl" in promoted_outputs
    assert "data/analysis/reports/*.md" in promoted_outputs


def test_regression_voi_manifest_declares_route_order() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    routes = {_string_value(route["id"]): route for route in _object_list(manifest["pipeline_routes"])}

    assert list(routes) == ["simulation_to_regression", "regression_to_voi"]
    first_route = _string_map(routes["simulation_to_regression"]["handoff"])
    second_route = _string_map(routes["regression_to_voi"]["handoff"])
    assert first_route["from"] == "rulespec-nz"
    assert first_route["to"] == "mars"
    assert second_route["from"] == "mars"
    assert second_route["to"] == "voiage"
