from __future__ import annotations

import json
from pathlib import Path
from typing import cast


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data/microsimulation/synthetic-population-builder.json"
FIXTURE_PATH = ROOT / "data/microsimulation/fixtures/synthetic-population-smoke.jsonl"
REQUIREMENTS_PATH = ROOT / "conductor/requirements_and_design.md"
BACKLOG_PATH = ROOT / "data/coverage/full-country-backlog.json"


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


def _backlog_track_ids() -> set[str]:
    backlog = _load_json_object(BACKLOG_PATH)
    return {_string_value(track["id"]) for track in _object_list(backlog["tracks"])}


def test_synthetic_population_builder_manifest_covers_track8_requirements() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    requirements = REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert manifest["track_id"] == "08_microsimulation_populations"
    assert manifest["builder_id"] == "synthetic-population-builder"
    assert manifest["authority"] == "adapter_contract"
    assert manifest["mode"] == "read_only_external_generators"
    assert "open_social_data" in requirements
    assert "fyi-cli" in requirements

    source_ids = {_string_value(source["id"]) for source in _object_list(manifest["sources"])}
    assert source_ids == {"open_social_data", "fyi-cli"}

    for source in _object_list(manifest["sources"]):
        assert source["status"] == "expected_local_external"
        assert _string_value(source["local_path_env"]).startswith("RULESPEC_NZ_")
        assert source["never_commit_payloads"] is True


def test_synthetic_population_builder_targets_backlog_policy_surfaces() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    backlog_ids = _backlog_track_ids()
    target_tracks = set(_string_list(manifest["target_policy_tracks"]))

    assert {
        "tax-personal-income",
        "levies-acc",
        "family-assistance-wff",
        "social-security-main-benefits",
        "housing-assistance",
        "superannuation",
    } <= target_tracks
    assert target_tracks <= backlog_ids


def test_synthetic_population_builder_arrow_contract_has_stable_entities() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    tables = {
        _string_value(table["id"]): table for table in _object_list(manifest["entity_tables"])
    }

    assert set(tables) == {"persons", "households", "benefit_units"}

    person_columns = _string_map(tables["persons"]["columns"])
    assert person_columns["person_id"] == "string"
    assert person_columns["household_id"] == "string"
    assert person_columns["age_years"] == "int16"
    assert person_columns["annual_employment_income"] == "decimal128(18,2)"
    assert tables["persons"]["primary_key"] == "person_id"

    household_columns = _string_map(tables["households"]["columns"])
    assert household_columns["household_id"] == "string"
    assert household_columns["region_code"] == "string"
    assert household_columns["tenure_type"] == "string"
    assert tables["households"]["primary_key"] == "household_id"

    benefit_unit_columns = _string_map(tables["benefit_units"]["columns"])
    assert benefit_unit_columns["benefit_unit_id"] == "string"
    assert benefit_unit_columns["household_id"] == "string"
    assert benefit_unit_columns["relationship_status"] == "string"
    assert tables["benefit_units"]["primary_key"] == "benefit_unit_id"


def test_synthetic_population_builder_rule_input_mapping_is_explicit() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    mappings = {
        _string_value(mapping["rulespec_input"]): mapping
        for mapping in _object_list(manifest["rulespec_input_mapping"])
    }

    assert mappings["input.person_age_years"]["table"] == "persons"
    assert mappings["input.annual_employment_income"]["column"] == "annual_employment_income"
    assert mappings["input.household_region_code"]["table"] == "households"
    assert mappings["input.relationship_status"]["table"] == "benefit_units"

    for mapping in mappings.values():
        assert _string_value(mapping["join_key"]) in {
            "person_id",
            "household_id",
            "benefit_unit_id",
        }


def test_synthetic_population_builder_privacy_and_repository_boundaries() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    privacy = manifest["privacy_boundaries"]
    repository = manifest["repository_boundaries"]
    assert isinstance(privacy, dict)
    assert isinstance(repository, dict)
    privacy_items = cast(dict[str, object], privacy)
    repository_items = cast(dict[str, object], repository)

    assert privacy_items["population_type"] == "synthetic_only"
    assert privacy_items["raw_personal_data_allowed"] is False
    assert privacy_items["direct_identifiers_allowed"] is False

    never_commit = set(_string_list(repository_items["never_commit_globs"]))
    assert "**/*.parquet" in never_commit
    assert "data/microsimulation/local/**" in never_commit
    assert "data/microsimulation/raw/**" in never_commit

    promoted_outputs = set(_string_list(repository_items["allowed_promoted_outputs"]))
    assert "data/microsimulation/*.json" in promoted_outputs
    assert "data/microsimulation/fixtures/*.jsonl" in promoted_outputs


def _jsonl_objects(path: Path) -> list[dict[str, object]]:
    return [_load_json_line(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _load_json_line(line: str) -> dict[str, object]:
    loaded = cast(object, json.loads(line))
    assert isinstance(loaded, dict)
    return cast(dict[str, object], loaded)


def test_synthetic_population_builder_fixture_smoke_data_covers_entity_schemas() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    fixture_refs = _object_list(manifest["fixture_smoke_data"])
    assert len(fixture_refs) == 1

    fixture_ref = fixture_refs[0]
    assert fixture_ref["fixture_id"] == "synthetic-population-smoke"
    assert fixture_ref["path"] == FIXTURE_PATH.relative_to(ROOT).as_posix()
    assert fixture_ref["payload_format"] == "jsonl"
    assert fixture_ref["synthetic_only"] is True
    assert fixture_ref["contains_raw_personal_data"] is False

    entity_tables = {
        _string_value(table["id"]): table for table in _object_list(manifest["entity_tables"])
    }
    rows = _jsonl_objects(FIXTURE_PATH)
    assert len(rows) == 3

    rows_by_table = {_string_value(row["table"]): row for row in rows}
    assert set(rows_by_table) == set(entity_tables)

    for table_id, table in entity_tables.items():
        row = rows_by_table[table_id]
        assert row["fixture_id"] == fixture_ref["fixture_id"]
        assert row["synthetic_only"] is True
        values = cast(dict[str, object], row["values"])
        assert set(_string_map(table["columns"])) <= set(values)
        assert _string_value(table["primary_key"]) in values


def test_synthetic_population_builder_records_live_generator_validation_state() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    live_validation = cast(dict[str, object], manifest["live_generator_validation"])

    assert live_validation["validated_at"] == "2026-06-22"
    assert live_validation["status"] == "partial_blocked"
    assert _string_list(live_validation["blocking_reasons"]) != []

    sources = {
        _string_value(source["source_id"]): source
        for source in _object_list(live_validation["sources"])
    }
    assert set(sources) == {"open_social_data", "fyi-cli"}

    open_social_data = sources["open_social_data"]
    assert open_social_data["env_var_set"] is False
    assert open_social_data["validated"] is False
    assert open_social_data["repo_candidate_found"] is True
    assert open_social_data["candidate_status"] == "repo_found_no_compatible_entity_output"

    fyi_cli = sources["fyi-cli"]
    assert fyi_cli["env_var_set"] is False
    assert fyi_cli["validated"] is False
    assert fyi_cli["repo_candidate_found"] is True
    assert fyi_cli["candidate_status"] == "repo_found_no_generator_output"


def test_synthetic_population_builder_deferred_work_excludes_completed_track_phases() -> None:
    manifest = _load_json_object(MANIFEST_PATH)
    deferred_work = set(_string_list(manifest["deferred_work"]))

    assert (
        "Add tiny JSONL or Arrow-compatible synthetic fixtures for schema-level validation."
        not in deferred_work
    )
    assert (
        "Validate against real local open_social_data and fyi-cli outputs when available."
        not in deferred_work
    )
    assert deferred_work == {
        "Add calibration diagnostics before any country-scale simulation run."
    }
