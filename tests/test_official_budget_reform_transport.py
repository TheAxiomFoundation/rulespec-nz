from __future__ import annotations

import json
import os
import subprocess
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "nz/policies/budget/official_budget_reform_replication.yaml"
MODULE_TEST = MODULE.with_name("official_budget_reform_replication.test.yaml")
PROGRAM = ROOT / "nz/programs/official_budget_reform_replication.yaml"
CONTRACT = ROOT / "data/microsimulation/official-budget-reform-transport.json"
SOURCE = (
    ROOT
    / "data/corpus/provisions/nz/policy/2026-08-29-treasury-official-budget-reforms.jsonl"
)

TARGET_INPUTS = {
    "family_tax_credit_eldest_dependent_child_care_units",
    "family_tax_credit_subsequent_dependent_child_care_units",
    "family_tax_credit_entitlement_days",
    "wff_family_scheme_income_for_relationship_period",
    "wff_family_credit_abatement_days",
    "entitled_to_in_work_tax_credit",
    "in_work_tax_credit_allowed_children_count",
    "in_work_tax_credit_weekly_periods",
    "child_tax_credit_for_entitlement_period",
    "parental_tax_credit_for_entitlement_period",
    "parental_tax_credit_additional_abatement",
}

PADDING_INPUTS = {
    "best_start_abatement_days",
    "best_start_child_care_fraction",
    "best_start_entitlement_days",
    "best_start_family_scheme_income_for_relationship_period",
    "minimum_family_adjusted_income_tax_liability",
    "minimum_family_amount_paid",
    "minimum_family_amount_received",
    "minimum_family_full_time_earner_weeks",
    "minimum_family_scheme_income_attributable_to_full_time_weeks",
    "minimum_family_tax_credit_weekly_periods",
}

OUTPUT_IDS = {
    "nz:policies/budget/official_budget_reform_replication#budget_2025_wff_abatement_entitlement_change",
    "nz:policies/budget/official_budget_reform_replication#budget_2026_iwtc_entitlement_change",
}


def _json(path: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", json.loads(path.read_text(encoding="utf-8")))


def _yaml(path: Path) -> dict[str, Any]:
    return cast("dict[str, Any]", yaml.safe_load(path.read_text(encoding="utf-8")))


@pytest.mark.unit
def test_program_selects_the_two_official_budget_entitlement_outputs() -> None:
    program = _yaml(PROGRAM)
    assert program == {
        "program": "nz/official-budget-reform-replication",
        "period": "2026-04-01/2027-03-31",
        "outputs": [
            "budget_2025_wff_abatement_entitlement_change",
            "budget_2026_iwtc_entitlement_change",
        ],
        "scope": {"nz": ["policies/budget/official_budget_reform_replication"]},
    }


@pytest.mark.unit
def test_rule_module_imports_the_enacted_wff_calculation() -> None:
    module = _yaml(MODULE)
    assert module["imports"] == ["nz:statutes/income_tax/family_scheme/tax_credits"]
    rules = {rule["name"]: rule for rule in module["rules"]}
    assert (
        rules["budget_2025_wff_abatement_baseline_threshold"]["versions"][0]["formula"]
        == "42700"
    )
    assert (
        rules["budget_2025_wff_abatement_baseline_rate"]["versions"][0]["formula"]
        == "0.27"
    )
    assert (
        rules["budget_pre_2026_iwtc_base_annual_amount"]["versions"][0]["formula"]
        == "5070"
    )
    assert {
        "budget_2025_wff_abatement_entitlement_change",
        "budget_2026_iwtc_entitlement_change",
    } <= set(rules)


@pytest.mark.unit
def test_transport_contract_is_exhaustive_and_fail_closed() -> None:
    contract = _json(CONTRACT)
    runtime = cast("dict[str, Any]", contract["runtime"])
    assert runtime["minimum_verified_engine_version"] == "0.2.2"
    assert (
        runtime["verified_engine_commit"] == "bb4b5684870547756078a62f1866a77c5b56f7f3"
    )
    inputs = cast("dict[str, Any]", contract["input_contract"])
    required = {
        item["name"]
        for item in cast("list[dict[str, Any]]", inputs["required_target_inputs"])
    }
    padding = {
        item["name"]
        for item in cast("list[dict[str, Any]]", inputs["adapter_padding_defaults"])
    }

    assert inputs["engine_root_input_count"] == 21
    assert required == TARGET_INPUTS
    assert padding == PADDING_INPUTS
    assert required.isdisjoint(padding)
    assert len(required | padding) == inputs["engine_root_input_count"]
    assert all(
        item["missing"] == "fail_closed"
        for item in cast("list[dict[str, Any]]", inputs["required_target_inputs"])
    )
    assert (
        contract["readiness"]["source_release"] == "pending_treasury_corpus_publication"
    )


@pytest.mark.unit
def test_transport_contract_has_family_entities_weights_and_outputs() -> None:
    contract = _json(CONTRACT)
    frame = cast("dict[str, Any]", contract["frame_schema"])
    assert frame["entities"] == ["person", "household", "family"]
    assert frame["engine_entity_names"] == {
        "person": "Person",
        "household": "Household",
        "family": "Family",
    }
    assert "person_family_id" in frame["structural_columns"]["person"]
    assert "family_household_id" in frame["structural_columns"]["family"]

    weights = cast("dict[str, Any]", contract["weight_contract"])
    assert weights["stored_weight_column"] == "household_weight"
    assert weights["family_weight_column_stored"] is False
    assert "resolve_weights('family')" in weights["family_weight_resolution"]

    outputs = cast("dict[str, Any]", contract["output_contract"])
    assert {item["id"] for item in outputs["requested"]} == OUTPUT_IDS
    assert all(item["entity"] == "family" for item in outputs["requested"])


@pytest.mark.unit
def test_rule_inventory_routes_budget_policy_to_official_agency_tables() -> None:
    inventory = _json(ROOT / "data/coverage/rulespec-rule-inventory.json")
    modules = cast("list[dict[str, Any]]", inventory["modules"])
    module = next(
        item for item in modules if item["path"] == MODULE.relative_to(ROOT).as_posix()
    )
    assert module["authority"] == "official_agency_table"
    assert module["source_route"] == "official_agency_table"


@pytest.mark.unit
def test_official_source_extracts_pin_pages_and_hashes() -> None:
    rows = [
        json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines()
    ]
    assert {row["citation_path"] for row in rows} == {
        "nz/policy/treasury/budget-2025/working-for-families-abatement-changes",
        "nz/policy/treasury/budget-2026/temporary-in-work-tax-credit-increase",
    }
    assert all(row["jurisdiction"] == "nz" for row in rows)
    assert all(row["document_class"] == "policy" for row in rows)
    assert rows[0]["source_sha256"]["summary"] == (
        "e6f1e2dcd14665f0728a9f7cf5cff736637ea94152337deb108c18094c9bedec"
    )
    assert rows[1]["source_sha256"]["summary"] == (
        "4e82abcf7ef2b605ff7cd6eb75a63826a2c6c18b84fd9cea1b2ceb9a19eda0ae"
    )
    assert rows[0]["source_pages"] == {
        "summary_pdf": 72,
        "summary_printed": 66,
        "fiscal_recommendation_pdf": 16,
        "fiscal_recommendation_printed": 14,
    }
    assert rows[1]["source_pages"] == {"summary_pdf": 55, "summary_printed": 49}


@pytest.mark.unit
def test_treasury_policy_citations_remain_pending_corpus_publication() -> None:
    rows = [
        json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines()
    ]
    paths = {row["citation_path"] for row in rows}
    module = _yaml(MODULE)
    assert module["module"]["source_verification"]["corpus_citation_path"] in paths
    atoms = [
        atom
        for rule in module["rules"]
        for atom in rule["metadata"]["proof"]["atoms"]
        if "/treasury/" in atom["source"]["corpus_citation_path"]
    ]
    assert {atom["source"]["corpus_citation_path"] for atom in atoms} == paths
    ledger = _json(ROOT / "data/corpus/canonical-provenance-migration-blockers.json")
    blockers = [
        entry for entry in ledger["blockers"] if entry["citation_path"] in paths
    ]
    assert {entry["citation_path"] for entry in blockers} == paths
    assert all(
        entry["blocker_kind"] == "local_official_extract_pending_release"
        for entry in blockers
    )
    assert sum(entry["blocked_proof_atom_count"] for entry in blockers) == len(atoms)
    assert len(atoms) == 12


@pytest.mark.unit
def test_companion_cases_lock_the_isolated_measure_deltas() -> None:
    cases = cast("list[dict[str, Any]]", yaml.safe_load(MODULE_TEST.read_text()))
    by_name = {case["name"]: case for case in cases}
    budget_2025 = by_name[
        "budget_2025_abatement_change_isolated_from_later_iwtc_measure"
    ]["output"]
    budget_2026 = by_name[
        "budget_2026_iwtc_change_respects_wff_abatement_and_credit_floor"
    ]["output"]
    assert (
        budget_2025[
            "nz:policies/budget/official_budget_reform_replication#budget_2025_wff_abatement_entitlement_change"
        ]
        == 568.5
    )
    assert (
        budget_2026[
            "nz:policies/budget/official_budget_reform_replication#budget_2026_iwtc_entitlement_change"
        ]
        == 438.5
    )


def _typed_value(slot: str, value: object) -> dict[str, object]:
    if slot == "entitled_to_in_work_tax_credit":
        return {"kind": "bool", "value": bool(value)}
    integer_slots = {
        "best_start_abatement_days",
        "best_start_entitlement_days",
        "family_tax_credit_entitlement_days",
        "in_work_tax_credit_allowed_children_count",
        "in_work_tax_credit_weekly_periods",
        "minimum_family_full_time_earner_weeks",
        "minimum_family_tax_credit_weekly_periods",
        "wff_family_credit_abatement_days",
    }
    if slot in integer_slots:
        return {"kind": "integer", "value": int(cast("int | float", value))}
    return {"kind": "decimal", "value": str(value)}


@pytest.mark.e2e
def test_actual_axiom_runtime_compiles_and_executes_measure_deltas(
    tmp_path: Path,
) -> None:
    binary = os.environ.get("AXIOM_RULES_ENGINE_BIN")
    if binary is None:
        pytest.skip("set AXIOM_RULES_ENGINE_BIN to run the Axiom runtime proof")

    artifact = tmp_path / "official-budget.compiled.json"
    compile_result = subprocess.run(  # noqa: S603
        [
            binary,
            "compile",
            "--program",
            str(MODULE),
            "--rulespec-root",
            str(ROOT),
            "--output",
            str(artifact),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert compile_result.returncode == 0, compile_result.stderr

    compiled = _json(artifact)
    catalog = {
        item["slot"]: item["canonical_request_name"]
        for item in compiled["metadata"]["input_catalog"]
    }
    assert set(catalog) == TARGET_INPUTS | PADDING_INPUTS

    companion_cases = cast(
        "list[dict[str, Any]]",
        yaml.safe_load(MODULE_TEST.read_text()),
    )
    families = {
        f"family:case-{index}": case for index, case in enumerate(companion_cases)
    }
    assert len(families) == 5
    inputs = []
    queries = []
    for entity_id, case in families.items():
        overrides = {
            name.split("#input.", 1)[1]: value for name, value in case["input"].items()
        }
        assert set(overrides) == TARGET_INPUTS
        values: dict[str, object] = dict.fromkeys(PADDING_INPUTS, 0)
        values.update(overrides)
        interval = {key: case["period"][key] for key in ("start", "end")}
        inputs.extend(
            {
                "name": catalog[slot],
                "entity": "Family",
                "entity_id": entity_id,
                "interval": interval,
                "value": _typed_value(slot, value),
            }
            for slot, value in values.items()
        )
        assert set(case["output"]) >= OUTPUT_IDS
        queries.append(
            {
                "entity_id": entity_id,
                "period": case["period"],
                "outputs": sorted(case["output"]),
            },
        )
    request = {
        "mode": "fast",
        "dataset": {"inputs": inputs, "relations": []},
        "queries": queries,
    }
    run_result = subprocess.run(  # noqa: S603
        [binary, "run-compiled", "--artifact", str(artifact)],
        input=json.dumps(request),
        check=False,
        capture_output=True,
        text=True,
    )
    assert run_result.returncode == 0, run_result.stderr
    response = cast("dict[str, Any]", json.loads(run_result.stdout))
    results = {result["entity_id"]: result["outputs"] for result in response["results"]}
    assert set(results) == set(families)
    for entity_id, case in families.items():
        for output, expected in case["output"].items():
            actual = results[entity_id][output]["value"]
            assert actual["kind"] == "decimal", (case["name"], output, actual)
            assert Decimal(actual["value"]) == Decimal(str(expected)), (
                case["name"],
                output,
                actual,
            )
