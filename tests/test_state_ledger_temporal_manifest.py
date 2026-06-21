from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/ledger/state-ledger-temporal-policy.json"
ORACLE_INDEX_PATH = ROOT / "data/oracles/oracle-index.json"
REQUIREMENTS_PATH = ROOT / "conductor/requirements_and_design.md"
NZ_LEGISLATION_INGESTION_PATH = ROOT / "data/corpus/ingestion/nz-legislation.json"


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


def _oracle_ids() -> set[str]:
    oracle_index = _load_json_object(ORACLE_INDEX_PATH)
    return {_string_value(oracle["id"]) for oracle in _object_list(oracle_index["oracles"])}


def test_state_ledger_manifest_covers_track10_requirements() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert manifest["track_id"] == "10_state_ledger_temporal"
    assert manifest["ledger_id"] == "state-ledger-temporal-policy"
    assert manifest["authority"] == "adapter_contract"
    assert manifest["mode"] == "read_only_external_ledger_tools"
    assert "kairos" in requirements
    assert "TheAxiomFoundation" in requirements

    tool_ids = {_string_value(tool["id"]) for tool in _object_list(manifest["tools"])}
    assert tool_ids == {"kairos", "axiom-corpus"}


def test_state_ledger_manifest_keeps_registry_status_explicit() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    ingestion = _load_json_object(NZ_LEGISLATION_INGESTION_PATH)
    oracle_ids = _oracle_ids()
    tools = {_string_value(tool["id"]): tool for tool in _object_list(manifest["tools"])}
    adapter = ingestion["adapter"]
    assert isinstance(adapter, dict)
    adapter_items = cast(dict[str, object], adapter)

    assert tools["kairos"]["oracle_id"] == "kairos"
    assert tools["kairos"]["oracle_id"] in oracle_ids
    assert tools["kairos"]["status"] == "pinned_research_oracle"

    assert tools["axiom-corpus"]["repository"] == "TheAxiomFoundation/axiom-corpus"
    assert tools["axiom-corpus"]["repository"] == adapter_items["repository"]
    assert tools["axiom-corpus"]["status"] == "pinned_ingestion_tool"
    assert tools["axiom-corpus"]["minimum_ref"] == adapter_items["minimum_ref"]


def test_state_ledger_manifest_temporal_event_contract_is_stable() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    event_types = {
        _string_value(event_type["id"]): event_type
        for event_type in _object_list(manifest["event_types"])
    }

    assert set(event_types) == {
        "policy_version_declared",
        "source_corpus_promoted",
        "rulespec_module_encoded",
        "oracle_parity_checked",
    }
    assert set(_string_list(manifest["event_statuses"])) == {
        "draft",
        "active",
        "superseded",
        "withdrawn",
    }

    required_fields = {
        "event_id",
        "event_type",
        "effective_from",
        "recorded_at",
        "source_ref",
        "artifact_path",
        "commit_sha",
    }
    for event_type in event_types.values():
        assert required_fields <= set(_string_list(event_type["required_fields"]))


def test_state_ledger_manifest_links_existing_contract_manifests() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    inputs = {_string_value(item["path"]) for item in _object_list(manifest["input_manifests"])}

    assert inputs == {
        "data/corpus/ingestion/nz-legislation.json",
        "data/corpus/ingestion/local-parquet-layers.json",
        "data/microsimulation/synthetic-population-builder.json",
        "data/analysis/regression-voi-pipeline.json",
    }
    for input_path in inputs:
        assert (ROOT / input_path).exists()

    assert manifest["source_spine_path"] == "data/corpus/inventory/nz/source-spine.json"
    assert (ROOT / _string_value(manifest["source_spine_path"])).exists()


def test_state_ledger_manifest_output_and_repository_boundaries() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    outputs = {_string_value(output["id"]): output for output in _object_list(manifest["outputs"])}
    boundaries = manifest["repository_boundaries"]
    assert isinstance(boundaries, dict)
    boundary_items = cast(dict[str, object], boundaries)

    assert set(outputs) == {"state_ledger_events", "temporal_policy_index", "handoff_report"}
    assert outputs["state_ledger_events"]["format"] == "jsonl"
    assert outputs["state_ledger_events"]["path"] == "data/ledger/events/<run-id>.jsonl"
    assert outputs["temporal_policy_index"]["format"] == "json"
    assert outputs["temporal_policy_index"]["path"] == "data/ledger/indexes/temporal-policy-index.json"
    assert outputs["handoff_report"]["format"] == "markdown"

    never_commit = set(_string_list(boundary_items["never_commit_globs"]))
    assert "data/ledger/local/**" in never_commit
    assert "data/ledger/raw/**" in never_commit
    assert "**/*.parquet" in never_commit
    assert "**/*.arrow" in never_commit

    promoted_outputs = set(_string_list(boundary_items["allowed_promoted_outputs"]))
    assert "data/ledger/*.json" in promoted_outputs
    assert "data/ledger/events/*.jsonl" in promoted_outputs
    assert "data/ledger/indexes/*.json" in promoted_outputs
    assert "data/ledger/reports/*.md" in promoted_outputs


def test_state_ledger_manifest_has_temporal_join_keys() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    joins = {_string_value(join["id"]): join for join in _object_list(manifest["temporal_join_keys"])}

    assert set(joins) == {
        "rulespec_module_to_corpus",
        "source_version_to_effective_interval",
        "policy_event_to_analysis_run",
    }
    assert {"citation_path", "artifact_path", "commit_sha"} <= set(
        _string_list(joins["rulespec_module_to_corpus"]["keys"])
    )
    assert {"citation_path", "effective_from", "effective_to"} <= set(
        _string_list(joins["source_version_to_effective_interval"]["keys"])
    )
    assert {"run_id", "scenario_id", "commit_sha"} <= set(
        _string_list(joins["policy_event_to_analysis_run"]["keys"])
    )


def _jsonl_objects(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        loaded = cast(object, json.loads(line))
        assert isinstance(loaded, dict)
        rows.append(cast(dict[str, object], loaded))
    return rows


def test_state_ledger_fixture_outputs_cover_event_schemas() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    event_types = {_string_value(item["id"]): item for item in _object_list(manifest["event_types"])}
    fixture_outputs = {_string_value(item["id"]): item for item in _object_list(manifest["fixture_outputs"])}

    assert set(fixture_outputs) == {"state-ledger-events-smoke", "temporal-policy-index-smoke", "handoff-report-smoke"}
    for fixture in fixture_outputs.values():
        assert fixture["synthetic_only"] is True
        assert fixture["contains_raw_ledger_payload"] is False

    events_path = ROOT / _string_value(fixture_outputs["state-ledger-events-smoke"]["path"])
    index_path = ROOT / _string_value(fixture_outputs["temporal-policy-index-smoke"]["path"])
    report_path = ROOT / _string_value(fixture_outputs["handoff-report-smoke"]["path"])

    events = _jsonl_objects(events_path)
    assert {_string_value(event["event_type"]) for event in events} == set(event_types)
    assert {_string_value(event["event_status"]) for event in events}.issubset(set(_string_list(manifest["event_statuses"])))
    for event in events:
        event_type = event_types[_string_value(event["event_type"])]
        assert set(_string_list(event_type["required_fields"])).issubset(set(event))

    index = _load_json_object(index_path)
    assert index["source_spine_path"] == manifest["source_spine_path"]
    assert set(_string_list(index["event_ids"])) == {_string_value(event["event_id"]) for event in events}

    report_text = report_path.read_text(encoding="utf-8").lower()
    for section in _string_list(fixture_outputs["handoff-report-smoke"]["required_sections"]):
        assert section in report_text
