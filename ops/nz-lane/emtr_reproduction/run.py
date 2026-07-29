#!/usr/bin/env python3
"""Reproduce the pinned NZ Treasury IncomeExplorer comparison with RuleSpec NZ.

This is intentionally a standard-library-only validation harness.  It compiles
the external composition with the pinned Axiom Rules Engine, evaluates the
statute-grounded modules in explain mode, aligns their periods to Treasury's
weekly output convention, and writes deterministic machine-readable artifacts.

The harness does not alter RuleSpec parameters to resemble the Treasury
forecast vintage.  The only Treasury-specific policy-flow convention retained
on the RuleSpec side is the raw IncomeExplorer IWTC branch threshold; it is
reported explicitly in the output metadata and never injected as a RuleSpec
parameter.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, getcontext
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


getcontext().prec = 40

HERE = Path(__file__).resolve().parent
FOUNDATION_ROOT = HERE.parents[2]

DEFAULT_RULESPEC_ROOT = (
    FOUNDATION_ROOT / "_axiom-worktrees" / "rulespec-nz-emtr" / "rulespec-nz"
)
DEFAULT_ENGINE_ROOT = FOUNDATION_ROOT / "_worktrees" / "engine-release-clone"
DEFAULT_TREASURY_ROOT = (
    Path.home() / "_axiom-worktrees" / "nz-treasury-income-explorer"
)
DEFAULT_COMPOSITION = HERE / "composition.yaml"
DEFAULT_ORACLE_GENERATOR = HERE / "generate_treasury_emtr_snapshot_expanded.R"
DEFAULT_RSCRIPT = Path("/usr/local/bin/Rscript")
EXPANDED_ORACLE_NAME = "treasury-emtr-snapshot-expanded.json"

EXPECTED_RULESPEC_SHA = "89a7d25dc03a4d045348620283332de10b1047da"
EXPECTED_ENGINE_SHA = "d59969b53430ae2fd97eb4349d44ad23ce930d85"
EXPECTED_ORACLE_COMMIT = "741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b"
EXPECTED_PARAMETER_FILE = "inst/parameters/TY27_BEFU25.yaml"
EXPECTED_PARAMETER_SHA256 = (
    "de89898c78989e057bde7d006b725fed4615ff32731ad008b96148c5a74b683c"
)
EXPECTED_MODEL_YEAR = 2027
EXPECTED_PERIOD_START = "2026-04-01"
EXPECTED_PERIOD_END = "2027-03-31"
EXPECTED_EXPANDED_GENERATED_AT = "2026-07-29"
EXPECTED_SAMPLE_WAGES = (0, 160, 250, 370, 555, 740, 1000, 1500)
ORIGINAL_SCENARIOS = (
    "single_parent_three_children_area1_rent",
    "couple_two_children_area2_mortgage",
    "couple_one_child_partner_10h_area3_rent",
    "single_no_children_area2_no_housing_costs",
)
EXPANDED_SCENARIOS = (
    "lone_parent_two_teens_jss",
    "couple_two_best_start_children_binding",
    "couple_two_children_dual_full_time",
    "single_childless_ietc_focused",
    "lone_parent_two_children_area4_high_rent_cap",
    "couple_childless_boarder_proxy",
    "large_family_four_children_age_bands",
)
EXPECTED_SCENARIOS = ORIGINAL_SCENARIOS + EXPANDED_SCENARIOS
EXPECTED_OUTPUT_COLUMNS = (
    "gross_wage1",
    "hours1",
    "gross_wage1_annual",
    "gross_wage2",
    "wage1_tax",
    "wage1_ACC_levy",
    "net_wage1",
    "net_wage",
    "net_benefit",
    "FTC_abated",
    "IWTC_abated",
    "MFTC",
    "IETC_abated",
    "WinterEnergy",
    "BestStart_Total",
    "AS_Amount",
    "WFF_abated",
    "Net_Income",
    "Net_Income_annual",
    "EMTR",
    "RR",
    "PTR",
)

# IncomeExplorer TY27_BEFU25 raw branch:
# FamilyAssistance_IWTC_IncomeThreshold_{Single,Couple} / 52.2.
# This remains a scenario-flow convention only; it is not a RuleSpec parameter.
ORACLE_IWTC_ANNUAL_THRESHOLD = Decimal("1226.7")
ORACLE_IWTC_THRESHOLD_DIVISOR = Decimal("52.2")
ORACLE_IWTC_WEEKLY_THRESHOLD = (
    ORACLE_IWTC_ANNUAL_THRESHOLD / ORACLE_IWTC_THRESHOLD_DIVISOR
)
ORACLE_ACC_WEEKLY_RATE = Decimal("0.0175")

D0 = Decimal(0)
D1 = Decimal(1)
D7 = Decimal(7)
D52 = Decimal(52)
D365 = Decimal(365)
WEEKS_IN_MODEL_YEAR = D365 / D7
ENGINE_DECIMAL_TOLERANCE = Decimal("0.000000000000000001")
ORACLE_SIX_DECIMAL_TOLERANCE = Decimal("0.0000005")

TAX_MODULE = "nz:statutes/income_tax/schedule_1/individual_income_tax"
ACC_MODULE = "nz:regulations/acc/earners_levy"
ELIGIBILITY_MODULE = "nz:statutes/income_tax/family_scheme/eligibility"
FSI_MODULE = "nz:statutes/income_tax/family_scheme/family_scheme_income"
WFF_MODULE = "nz:statutes/income_tax/family_scheme/tax_credits"
IETC_MODULE = "nz:statutes/income_tax/credits/individual_credits"
BENEFIT_MODULE = "nz:statutes/social_security/main_benefits/rates"
WEP_MODULE = "nz:statutes/social_security/winter_energy_payment/core"
AS_MODULE = "nz:statutes/social_security/accommodation_supplement/core"


class HarnessError(RuntimeError):
    """A deterministic precondition or engine-evaluation failure."""


def dec(value: Any) -> Decimal:
    """Convert a JSON/Python numeric value to Decimal without binary drift."""

    if isinstance(value, Decimal):
        return value
    if value is None:
        raise HarnessError("cannot convert null to Decimal")
    return Decimal(str(value))


def decimal_text(value: Decimal) -> str:
    """Stable non-exponent decimal text with insignificant zeros removed."""

    if value.is_zero():
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def json_number(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_checked(
    argv: Sequence[str],
    *,
    stdin: str | None = None,
    cwd: Path | None = None,
    label: str,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        list(argv),
        input=stdin,
        text=True,
        capture_output=True,
        cwd=cwd,
        check=False,
    )
    if process.returncode:
        stderr = process.stderr.strip()
        stdout = process.stdout.strip()
        detail = stderr or stdout or f"exit status {process.returncode}"
        raise HarnessError(f"{label} failed: {detail}")
    return process


def git_sha(root: Path) -> str:
    return run_checked(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        label=f"git SHA check for {root}",
    ).stdout.strip()


def git_tracked_dirty(root: Path) -> bool:
    status = run_checked(
        [
            "git",
            "-C",
            str(root),
            "status",
            "--porcelain",
            "--untracked-files=no",
        ],
        label=f"git status check for {root}",
    ).stdout
    return bool(status.strip())


def require_file(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise HarnessError(f"{label} does not exist: {resolved}")
    return resolved


def require_directory(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise HarnessError(f"{label} does not exist: {resolved}")
    return resolved


def output_id(module: str, rule: str) -> str:
    return f"{module}#{rule}"


@dataclass(frozen=True)
class Provenance:
    oracle_path: Path
    oracle_sha256: str
    baseline_oracle_path: Path
    baseline_oracle_sha256: str
    oracle_generator_path: Path
    oracle_generator_sha256: str
    rscript_path: Path
    rscript_version: str
    rulespec_root: Path
    rulespec_sha: str
    rulespec_tracked_dirty: bool
    engine_root: Path
    engine_sha: str
    engine_tracked_dirty: bool
    engine_binary: Path
    engine_binary_sha256: str
    composition_path: Path
    composition_sha256: str
    treasury_root: Path
    treasury_present: bool
    treasury_sha: str | None
    treasury_parameter_sha256: str | None

    def as_json(self) -> dict[str, Any]:
        return {
            "oracle_snapshot": {
                "path": str(self.oracle_path),
                "sha256": self.oracle_sha256,
                "generated_at": EXPECTED_EXPANDED_GENERATED_AT,
            },
            "baseline_oracle_regeneration": {
                "path": str(self.baseline_oracle_path),
                "sha256": self.baseline_oracle_sha256,
                "byte_identical": True,
            },
            "oracle_generator": {
                "path": str(self.oracle_generator_path),
                "sha256": self.oracle_generator_sha256,
                "rscript": str(self.rscript_path),
                "rscript_version": self.rscript_version,
            },
            "rulespec": {
                "root": str(self.rulespec_root),
                "git_sha": self.rulespec_sha,
                "expected_git_sha": EXPECTED_RULESPEC_SHA,
                "tracked_dirty": self.rulespec_tracked_dirty,
            },
            "engine": {
                "root": str(self.engine_root),
                "git_sha": self.engine_sha,
                "expected_git_sha": EXPECTED_ENGINE_SHA,
                "tracked_dirty": self.engine_tracked_dirty,
                "binary": str(self.engine_binary),
                "binary_sha256": self.engine_binary_sha256,
            },
            "composition": {
                "path": str(self.composition_path),
                "sha256": self.composition_sha256,
            },
            "treasury_checkout": {
                "root": str(self.treasury_root),
                "present": self.treasury_present,
                "git_sha": self.treasury_sha,
                "parameter_file": EXPECTED_PARAMETER_FILE,
                "parameter_sha256": self.treasury_parameter_sha256,
            },
        }


@dataclass(frozen=True)
class RegeneratedOracle:
    oracle: dict[str, Any]
    expanded_text: str
    baseline_oracle_path: Path
    baseline_oracle_sha256: str
    generator_path: Path
    rscript_path: Path
    rscript_version: str


def regenerate_treasury_oracles(
    *,
    rulespec_root: Path,
    treasury_root: Path,
    oracle_generator: Path,
    rscript: Path,
) -> RegeneratedOracle:
    baseline_oracle_path = require_file(
        rulespec_root / "data" / "oracles" / "treasury-emtr-snapshot.json",
        "pinned Treasury baseline oracle",
    )
    treasury_root = require_directory(
        treasury_root, "Treasury source checkout"
    )
    oracle_generator = require_file(
        oracle_generator, "Treasury oracle generator"
    )
    rscript = require_file(rscript, "Rscript 4.3.0")
    parameter_path = require_file(
        treasury_root / EXPECTED_PARAMETER_FILE,
        "Treasury parameter file",
    )

    treasury_sha = git_sha(treasury_root)
    if treasury_sha != EXPECTED_ORACLE_COMMIT:
        raise HarnessError(
            f"Treasury checkout SHA mismatch: expected {EXPECTED_ORACLE_COMMIT}, "
            f"found {treasury_sha}"
        )
    parameter_sha = sha256_file(parameter_path)
    if parameter_sha != EXPECTED_PARAMETER_SHA256:
        raise HarnessError(
            "Treasury parameter SHA-256 mismatch: expected "
            f"{EXPECTED_PARAMETER_SHA256}, found {parameter_sha}"
        )

    version_process = run_checked(
        [str(rscript), "--version"],
        label="Rscript version check",
    )
    rscript_version = "\n".join(
        part.strip()
        for part in (version_process.stdout, version_process.stderr)
        if part.strip()
    )
    if "version 4.3.0" not in rscript_version:
        raise HarnessError(
            "Treasury regeneration requires Rscript 4.3.0, found "
            f"{rscript_version!r}"
        )

    with tempfile.TemporaryDirectory(
        prefix="axiom-emtr-oracle-regeneration-"
    ) as raw_temp:
        temp_root = Path(raw_temp)
        baseline_output = temp_root / "baseline.json"
        expanded_output = temp_root / EXPANDED_ORACLE_NAME
        common_args = (
            str(rscript),
            str(oracle_generator),
            f"--repo={treasury_root}",
            f"--parameter-file={parameter_path}",
        )
        run_checked(
            [
                *common_args,
                "--mode=baseline",
                f"--output={baseline_output}",
            ],
            label="Treasury baseline oracle regeneration",
        )
        regenerated_baseline = baseline_output.read_bytes()
        pinned_baseline = baseline_oracle_path.read_bytes()
        if regenerated_baseline != pinned_baseline:
            raise HarnessError(
                "STOP: pinned Treasury baseline did not regenerate "
                "byte-for-byte; expected SHA-256 "
                f"{hashlib.sha256(pinned_baseline).hexdigest()}, found "
                f"{hashlib.sha256(regenerated_baseline).hexdigest()}"
            )
        run_checked(
            [
                *common_args,
                "--mode=expanded",
                f"--output={expanded_output}",
            ],
            label="expanded Treasury oracle regeneration",
        )
        expanded_text = expanded_output.read_text(encoding="utf-8")

    try:
        oracle = json.loads(expanded_text)
    except json.JSONDecodeError as exc:
        raise HarnessError(
            f"expanded Treasury generator emitted invalid JSON: {exc}"
        ) from exc
    return RegeneratedOracle(
        oracle=oracle,
        expanded_text=expanded_text,
        baseline_oracle_path=baseline_oracle_path,
        baseline_oracle_sha256=sha256_file(baseline_oracle_path),
        generator_path=oracle_generator,
        rscript_path=rscript,
        rscript_version=rscript_version,
    )


def verify_inputs(
    *,
    regenerated: RegeneratedOracle,
    rulespec_root: Path,
    engine_root: Path,
    engine_binary: Path,
    treasury_root: Path,
    composition_path: Path,
    oracle_generator: Path,
    rscript: Path,
) -> tuple[dict[str, Any], Provenance]:
    rulespec_root = require_directory(rulespec_root, "RuleSpec root")
    engine_root = require_directory(engine_root, "engine root")
    engine_binary = require_file(engine_binary, "engine binary")
    composition_path = require_file(composition_path, "composition")
    expected_engine_binary = (
        engine_root / "target" / "release" / "axiom-rules-engine"
    ).resolve()
    if engine_binary != expected_engine_binary:
        raise HarnessError(
            "engine binary must be the release binary under the pinned engine "
            f"checkout: expected {expected_engine_binary}, found {engine_binary}"
        )

    if rulespec_root.name != "rulespec-nz":
        raise HarnessError(
            f"RuleSpec root basename must be rulespec-nz, got {rulespec_root.name!r}"
        )

    oracle_generator = require_file(
        oracle_generator, "Treasury oracle generator"
    )
    rscript = require_file(rscript, "Rscript 4.3.0")
    oracle = regenerated.oracle
    oracle_path = (HERE / EXPANDED_ORACLE_NAME).resolve()
    with regenerated.baseline_oracle_path.open(encoding="utf-8") as source:
        baseline_oracle = json.load(source)

    pinned = oracle.get("oracle", {})
    checks: tuple[tuple[str, Any, Any], ...] = (
        (
            "generated_at",
            oracle.get("generated_at"),
            EXPECTED_EXPANDED_GENERATED_AT,
        ),
        ("oracle.commit", pinned.get("commit"), EXPECTED_ORACLE_COMMIT),
        (
            "oracle.parameter_file",
            pinned.get("parameter_file"),
            EXPECTED_PARAMETER_FILE,
        ),
        (
            "oracle.parameter_file_sha256",
            pinned.get("parameter_file_sha256"),
            EXPECTED_PARAMETER_SHA256,
        ),
        ("oracle.model_year", pinned.get("model_year"), EXPECTED_MODEL_YEAR),
        (
            "generator.adapter",
            oracle.get("generator", {}).get("adapter"),
            "treasury-income-explorer-emtr-snapshot-expanded",
        ),
        (
            "generator.sampled_weekly_gross_wage",
            tuple(oracle.get("generator", {}).get("sampled_weekly_gross_wage", ())),
            EXPECTED_SAMPLE_WAGES,
        ),
        (
            "generator.output_columns",
            tuple(oracle.get("generator", {}).get("output_columns", ())),
            EXPECTED_OUTPUT_COLUMNS,
        ),
        (
            "scenario ids",
            tuple(item.get("id") for item in oracle.get("scenarios", ())),
            EXPECTED_SCENARIOS,
        ),
    )
    for label, actual, expected in checks:
        if actual != expected:
            raise HarnessError(
                f"{label} mismatch: expected {expected!r}, found {actual!r}"
            )
    note = oracle.get("generator", {}).get("note")
    if note != "Treasury outputs are weekly unless the column name says annual.":
        raise HarnessError(f"unexpected generator.note: {note!r}")
    scenario_provenance = oracle.get("scenario_provenance", {})
    if tuple(scenario_provenance) != EXPECTED_SCENARIOS:
        raise HarnessError(
            "scenario provenance ids mismatch: expected "
            f"{EXPECTED_SCENARIOS!r}, found {tuple(scenario_provenance)!r}"
        )
    if oracle.get("scenarios", [])[: len(ORIGINAL_SCENARIOS)] != baseline_oracle.get(
        "scenarios", []
    ):
        raise HarnessError(
            "expanded oracle did not preserve the original four scenario "
            "objects byte-for-byte in value and schema"
        )
    for raw_scenario in oracle.get("scenarios", ()):
        scenario_id = str(raw_scenario["id"])
        scenario_metadata = scenario_provenance[scenario_id]
        displayed = tuple(
            int(value)
            for value in scenario_metadata.get(
                "displayed_weekly_gross_wage", ()
            )
        )
        if displayed != EXPECTED_SAMPLE_WAGES:
            raise HarnessError(
                f"{scenario_id} display wages changed: {displayed!r}"
            )
        additional = tuple(
            int(value)
            for value in scenario_metadata.get(
                "additional_weekly_gross_wage", ()
            )
        )
        expected_wages = tuple(sorted(set(displayed + additional)))
        actual_wages = tuple(
            int(dec(item["gross_wage1"]))
            for item in raw_scenario.get("sampled_outputs", ())
        )
        if actual_wages != expected_wages:
            raise HarnessError(
                f"{scenario_id} sampled wages mismatch: expected "
                f"{expected_wages!r}, found {actual_wages!r}"
            )

    rulespec_sha = git_sha(rulespec_root)
    engine_sha = git_sha(engine_root)
    if rulespec_sha != EXPECTED_RULESPEC_SHA:
        raise HarnessError(
            f"RuleSpec SHA mismatch: expected {EXPECTED_RULESPEC_SHA}, "
            f"found {rulespec_sha}"
        )
    if engine_sha != EXPECTED_ENGINE_SHA:
        raise HarnessError(
            f"engine SHA mismatch: expected {EXPECTED_ENGINE_SHA}, found {engine_sha}"
        )
    rulespec_dirty = git_tracked_dirty(rulespec_root)
    engine_dirty = git_tracked_dirty(engine_root)
    if rulespec_dirty:
        raise HarnessError(f"RuleSpec checkout has tracked modifications: {rulespec_root}")
    if engine_dirty:
        raise HarnessError(f"engine checkout has tracked modifications: {engine_root}")

    treasury_root = require_directory(treasury_root, "Treasury source checkout")
    treasury_present = True
    treasury_sha: str | None = git_sha(treasury_root)
    parameter_sha: str | None
    if treasury_sha != EXPECTED_ORACLE_COMMIT:
        raise HarnessError(
            f"Treasury checkout SHA mismatch: expected {EXPECTED_ORACLE_COMMIT}, "
            f"found {treasury_sha}"
        )
    parameter_path = require_file(
        treasury_root / EXPECTED_PARAMETER_FILE,
        "Treasury parameter file",
    )
    parameter_sha = sha256_file(parameter_path)
    if parameter_sha != EXPECTED_PARAMETER_SHA256:
        raise HarnessError(
            "Treasury parameter SHA-256 mismatch: expected "
            f"{EXPECTED_PARAMETER_SHA256}, found {parameter_sha}"
        )

    provenance = Provenance(
        oracle_path=oracle_path,
        oracle_sha256=hashlib.sha256(
            regenerated.expanded_text.encode("utf-8")
        ).hexdigest(),
        baseline_oracle_path=regenerated.baseline_oracle_path,
        baseline_oracle_sha256=regenerated.baseline_oracle_sha256,
        oracle_generator_path=oracle_generator,
        oracle_generator_sha256=sha256_file(oracle_generator),
        rscript_path=rscript,
        rscript_version=regenerated.rscript_version,
        rulespec_root=rulespec_root,
        rulespec_sha=rulespec_sha,
        rulespec_tracked_dirty=rulespec_dirty,
        engine_root=engine_root,
        engine_sha=engine_sha,
        engine_tracked_dirty=engine_dirty,
        engine_binary=engine_binary,
        engine_binary_sha256=sha256_file(engine_binary),
        composition_path=composition_path,
        composition_sha256=sha256_file(composition_path),
        treasury_root=treasury_root,
        treasury_present=treasury_present,
        treasury_sha=treasury_sha,
        treasury_parameter_sha256=parameter_sha,
    )
    return oracle, provenance


class Engine:
    """Small JSON-CLI adapter that always evaluates in explain mode."""

    def __init__(
        self,
        *,
        binary: Path,
        artifact: Path,
        catalog: Mapping[str, str],
    ) -> None:
        self.binary = binary
        self.artifact = artifact
        self.catalog = dict(catalog)
        self.call_count = 0

    @classmethod
    def compile(
        cls,
        *,
        binary: Path,
        composition: Path,
        rulespec_root: Path,
        artifact: Path,
    ) -> tuple["Engine", dict[str, Any], str]:
        process = run_checked(
            [
                str(binary),
                "compile-composed",
                "--program",
                str(composition),
                "--rulespec-root",
                str(rulespec_root),
                "--output",
                str(artifact),
            ],
            label="RuleSpec composition compile",
        )
        with artifact.open(encoding="utf-8") as source:
            compiled = json.load(source)
        catalog_entries = compiled.get("metadata", {}).get("input_catalog", [])
        catalog = {
            entry["slot"]: entry["canonical_request_name"]
            for entry in catalog_entries
        }
        if not catalog:
            raise HarnessError("compiled artifact has an empty input catalog")
        engine = cls(binary=binary, artifact=artifact, catalog=catalog)
        return engine, compiled, process.stdout.strip()

    def input_record(
        self,
        *,
        slot: str,
        value: bool | int | Decimal,
        entity: str,
        entity_id: str,
    ) -> dict[str, Any]:
        try:
            name = self.catalog[slot]
        except KeyError as exc:
            raise HarnessError(f"compiled input catalog has no slot {slot!r}") from exc
        if isinstance(value, bool):
            scalar = {"kind": "bool", "value": value}
        elif isinstance(value, int):
            scalar = {"kind": "integer", "value": value}
        elif isinstance(value, Decimal):
            scalar = {"kind": "decimal", "value": decimal_text(value)}
        else:
            raise HarnessError(
                f"unsupported input value type for {slot}: {type(value).__name__}"
            )
        return {
            "name": name,
            "entity": entity,
            "entity_id": entity_id,
            "interval": {
                "start": EXPECTED_PERIOD_START,
                "end": EXPECTED_PERIOD_END,
            },
            "value": scalar,
        }

    def evaluate(
        self,
        *,
        entity: str,
        entity_id: str,
        inputs: Mapping[str, bool | int | Decimal],
        outputs: Sequence[str],
    ) -> tuple[dict[str, Decimal | str], dict[str, Any]]:
        request = {
            "mode": "explain",
            "dataset": {
                "inputs": [
                    self.input_record(
                        slot=slot,
                        value=value,
                        entity=entity,
                        entity_id=entity_id,
                    )
                    for slot, value in sorted(inputs.items())
                ],
                "relations": [],
            },
            "queries": [
                {
                    "entity_id": entity_id,
                    "period": {
                        "period_kind": "tax_year",
                        "start": EXPECTED_PERIOD_START,
                        "end": EXPECTED_PERIOD_END,
                    },
                    "outputs": list(outputs),
                }
            ],
        }
        process = run_checked(
            [
                str(self.binary),
                "run-compiled",
                "--artifact",
                str(self.artifact),
            ],
            stdin=json.dumps(request, sort_keys=True, separators=(",", ":")),
            label=f"engine evaluation for {entity_id}",
        )
        self.call_count += 1
        try:
            response = json.loads(process.stdout)
        except json.JSONDecodeError as exc:
            raise HarnessError(
                f"engine returned invalid JSON for {entity_id}: {process.stdout!r}"
            ) from exc
        metadata = response.get("metadata", {})
        if (
            metadata.get("requested_mode") != "explain"
            or metadata.get("actual_mode") != "explain"
        ):
            raise HarnessError(
                f"engine did not execute {entity_id} in explain mode: {metadata!r}"
            )
        results = response.get("results", [])
        if len(results) != 1:
            raise HarnessError(
                f"expected one engine result for {entity_id}, found {len(results)}"
            )
        values: dict[str, Decimal | str] = {}
        returned = results[0].get("outputs", {})
        for target in outputs:
            if target not in returned:
                raise HarnessError(f"engine omitted requested output {target}")
            item = returned[target]
            if item.get("kind") == "judgment":
                values[target] = item["outcome"]
            elif item.get("kind") == "scalar":
                values[target] = dec(item["value"]["value"])
            else:
                raise HarnessError(f"unknown engine output shape for {target}: {item!r}")
        return values, results[0].get("trace", {})


def normalize_children(raw: Any) -> list[int]:
    if isinstance(raw, list):
        return [int(value) for value in raw]
    if isinstance(raw, (int, float)):
        return [int(raw)]
    if raw in ({}, None):
        return []
    raise HarnessError(f"unsupported Children_ages encoding: {raw!r}")


TAX_OUTPUT = output_id(TAX_MODULE, "individual_income_tax_before_credits")
ACC_OUTPUT = output_id(ACC_MODULE, "acc_standard_earners_levy_including_gst")
JOBSEEKER_OUTPUT = output_id(BENEFIT_MODULE, "jobseeker_support_net_weekly_payment")
SOLE_PARENT_OUTPUT = output_id(
    BENEFIT_MODULE, "sole_parent_support_net_weekly_payment"
)
FTC_OUTPUT = output_id(WFF_MODULE, "family_tax_credit_after_abatement")
IWTC_BEFORE_OUTPUT = output_id(WFF_MODULE, "in_work_tax_credit_before_abatement")
IWTC_REMAINING_ABATEMENT_OUTPUT = output_id(
    WFF_MODULE, "wff_abatement_remaining_after_family_tax_credit"
)
IWTC_ENTITLEMENT_OUTPUT = output_id(
    ELIGIBILITY_MODULE, "entitled_to_in_work_tax_credit"
)
MFTC_OUTPUT = output_id(WFF_MODULE, "minimum_family_tax_credit")
IETC_OUTPUT = output_id(IETC_MODULE, "independent_earner_tax_credit")
WEP_RATE_OUTPUT = output_id(
    WEP_MODULE, "winter_energy_payment_rate_per_winter_period"
)
BEST_START_OUTPUT = output_id(WFF_MODULE, "best_start_tax_credit")
BEST_START_BEFORE_OUTPUT = output_id(
    WFF_MODULE, "best_start_tax_credit_before_abatement"
)
BEST_START_ABATEMENT_OUTPUT = output_id(
    WFF_MODULE, "best_start_credit_abatement"
)
AS_UNROUNDED_OUTPUT = output_id(
    AS_MODULE, "accommodation_supplement_weekly_amount_before_rounding"
)
AS_ROUNDED_OUTPUT = output_id(
    AS_MODULE, "accommodation_supplement_rounded_weekly_payment"
)
FSI_OUTPUT = output_id(FSI_MODULE, "family_scheme_income")

COMPARISON_COLUMNS = (
    "gross_wage1",
    "hours1",
    "gross_wage1_annual",
    "gross_wage2",
    "wage1_tax",
    "wage1_ACC_levy",
    "net_wage1",
    "net_wage",
    "net_benefit",
    "FTC_abated",
    "IWTC_abated",
    "MFTC",
    "IETC_abated",
    "WinterEnergy",
    "BestStart_Total",
    "AS_Amount",
    "WFF_abated",
    "Net_Income",
    "Net_Income_annual",
    "EMTR",
)


@dataclass(frozen=True)
class Scenario:
    id: str
    description: str
    partnered: bool
    wage1_hourly: Decimal
    children: tuple[int, ...]
    gross_wage2: Decimal
    hours2: Decimal
    accommodation_costs: Decimal
    accommodation_rent: bool
    accommodation_area: int
    accommodation_boarder: bool
    weekly_board_and_lodgings_paid: Decimal
    sampled_wages: tuple[int, ...]

    @classmethod
    def from_oracle(
        cls,
        raw: Mapping[str, Any],
        provenance: Mapping[str, Any],
    ) -> "Scenario":
        inputs = raw["inputs"]
        rulespec_profile = provenance.get("rulespec_profile", {})
        displayed = tuple(
            int(value)
            for value in provenance.get(
                "displayed_weekly_gross_wage",
                EXPECTED_SAMPLE_WAGES,
            )
        )
        additional = tuple(
            int(value)
            for value in provenance.get(
                "additional_weekly_gross_wage",
                (),
            )
        )
        sampled_wages = tuple(sorted(set(displayed + additional)))
        return cls(
            id=str(raw["id"]),
            description=str(raw["description"]),
            partnered=bool(inputs["Partnered"]),
            wage1_hourly=dec(inputs["wage1_hourly"]),
            children=tuple(normalize_children(inputs["Children_ages"])),
            gross_wage2=dec(inputs["gross_wage2"]),
            hours2=dec(inputs["hours2"]),
            accommodation_costs=dec(inputs["AS_Accommodation_Costs"]),
            accommodation_rent=bool(inputs["AS_Accommodation_Rent"]),
            accommodation_area=int(inputs["AS_Area"]),
            accommodation_boarder=bool(
                rulespec_profile.get("boarder", False)
            ),
            weekly_board_and_lodgings_paid=dec(
                rulespec_profile.get("accommodation_cost", 0)
                if rulespec_profile.get("boarder", False)
                else 0
            ),
            sampled_wages=sampled_wages,
        )


def scalar_decimal(values: Mapping[str, Decimal | str], target: str) -> Decimal:
    value = values[target]
    if not isinstance(value, Decimal):
        raise HarnessError(f"expected scalar output {target}, found {value!r}")
    return value


def selected_parameter_values(
    compiled: Mapping[str, Any],
    name: str,
) -> dict[int, Decimal]:
    matches = [
        item
        for item in compiled["program"]["parameters"]
        if item.get("name") == name
    ]
    if len(matches) != 1:
        raise HarnessError(
            f"expected one compiled parameter named {name!r}, found {len(matches)}"
        )
    eligible = [
        version
        for version in matches[0]["versions"]
        if version["effective_from"] <= EXPECTED_PERIOD_START
    ]
    if not eligible:
        raise HarnessError(
            f"parameter {name!r} has no version at {EXPECTED_PERIOD_START}"
        )
    selected = max(eligible, key=lambda item: item["effective_from"])
    result: dict[int, Decimal] = {}
    for raw_index, raw_value in selected["values"].items():
        result[int(raw_index)] = dec(raw_value["value"])
    return result


class ModelEvaluator:
    """Host-level composition required by the relation-free compiled program."""

    def __init__(self, engine: Engine, compiled: Mapping[str, Any]) -> None:
        self.engine = engine
        self._cache: dict[
            tuple[
                tuple[tuple[str, str, str], ...],
                tuple[str, ...],
            ],
            dict[str, Decimal | str],
        ] = {}
        self._gross_benefit_cache: dict[Decimal, Decimal] = {}
        self._as_cutout_cache: dict[
            tuple[bool, int, bool], Decimal
        ] = {}
        self.tax_rates = selected_parameter_values(
            compiled, "individual_income_tax_bracket_rates"
        )
        self.tax_thresholds = selected_parameter_values(
            compiled, "individual_income_tax_bracket_thresholds"
        )
        self.ftc_eldest_annual = selected_parameter_values(
            compiled, "family_tax_credit_eldest_child_annual_amount"
        )[0]
        self.wff_abatement_threshold = selected_parameter_values(
            compiled, "wff_family_credit_abatement_threshold"
        )[0]
        self.wff_abatement_rate = selected_parameter_values(
            compiled, "wff_family_credit_abatement_rate"
        )[0]
        self.benefit_income_test_lower_threshold = selected_parameter_values(
            compiled, "main_benefit_income_test_lower_weekly_threshold"
        )[0]
        self.benefit_income_test_3_rate = selected_parameter_values(
            compiled, "main_benefit_income_test_3_abatement_rate"
        )[0]
        self.jobseeker_single_with_children_rate = selected_parameter_values(
            compiled,
            "jobseeker_support_single_with_dependent_children_weekly_rate",
        )[0]
        expected_rate_indexes = set(range(1, 6))
        expected_threshold_indexes = set(range(1, 5))
        if set(self.tax_rates) != expected_rate_indexes:
            raise HarnessError(
                f"unexpected tax-rate indexes: {sorted(self.tax_rates)}"
            )
        if set(self.tax_thresholds) != expected_threshold_indexes:
            raise HarnessError(
                f"unexpected tax-threshold indexes: {sorted(self.tax_thresholds)}"
            )

    def _evaluate(
        self,
        *,
        entity: str,
        entity_id: str,
        inputs: Mapping[str, bool | int | Decimal],
        outputs: Sequence[str],
    ) -> dict[str, Decimal | str]:
        cache_inputs = tuple(
            (
                slot,
                type(value).__name__,
                decimal_text(value) if isinstance(value, Decimal) else str(value),
            )
            for slot, value in sorted(inputs.items())
        )
        key = (cache_inputs, tuple(outputs))
        if key not in self._cache:
            values, _trace = self.engine.evaluate(
                entity=entity,
                entity_id=entity_id,
                inputs=inputs,
                outputs=outputs,
            )
            self._cache[key] = values
        return dict(self._cache[key])

    def tax_from_schedule(self, annual_income: Decimal) -> Decimal:
        income = max(D0, annual_income)
        tax = D0
        lower = D0
        for bracket in range(1, 5):
            upper = self.tax_thresholds[bracket]
            tax += max(D0, min(income, upper) - lower) * self.tax_rates[bracket]
            lower = upper
        tax += max(D0, income - lower) * self.tax_rates[5]
        return tax

    def annual_tax(self, annual_income: Decimal) -> Decimal:
        values = self._evaluate(
            entity="Person",
            entity_id=f"tax:{decimal_text(annual_income)}",
            inputs={"taxable_income": annual_income},
            outputs=[TAX_OUTPUT],
        )
        engine_tax = scalar_decimal(values, TAX_OUTPUT)
        schedule_tax = self.tax_from_schedule(annual_income)
        # The engine's JSON boundary emits fewer decimal places than the
        # 40-digit host context. This verifies the same schedule far below a
        # cent while retaining the engine value for every reported result.
        if abs(engine_tax - schedule_tax) > ENGINE_DECIMAL_TOLERANCE:
            raise HarnessError(
                "compiled tax schedule and engine output disagree at "
                f"{decimal_text(annual_income)}: "
                f"{decimal_text(schedule_tax)} != {decimal_text(engine_tax)}"
            )
        return engine_tax

    def annual_acc(self, annual_earnings: Decimal) -> Decimal:
        values = self._evaluate(
            entity="Person",
            entity_id=f"acc:{decimal_text(annual_earnings)}",
            inputs={"acc_earnings_for_earners_levy": annual_earnings},
            outputs=[ACC_OUTPUT],
        )
        return scalar_decimal(values, ACC_OUTPUT)

    def gross_benefit_from_net_weekly(self, net_weekly: Decimal) -> Decimal:
        if net_weekly <= 0:
            return D0
        if net_weekly in self._gross_benefit_cache:
            return self._gross_benefit_cache[net_weekly]
        annual_net = net_weekly * WEEKS_IN_MODEL_YEAR
        low = annual_net
        high = annual_net * 2 + Decimal("1000")
        while high - self.tax_from_schedule(high) < annual_net:
            high *= 2
        for _ in range(160):
            midpoint = (low + high) / 2
            if midpoint - self.tax_from_schedule(midpoint) < annual_net:
                low = midpoint
            else:
                high = midpoint
        gross_weekly = ((low + high) / 2) / WEEKS_IN_MODEL_YEAR
        residual = (
            gross_weekly
            - self.tax_from_schedule(gross_weekly * WEEKS_IN_MODEL_YEAR)
            / WEEKS_IN_MODEL_YEAR
            - net_weekly
        )
        if abs(residual) > Decimal("0.00000000000000000001"):
            raise HarnessError(
                "tax gross-up did not converge for weekly net benefit "
                f"{decimal_text(net_weekly)}: residual {decimal_text(residual)}"
            )
        self._gross_benefit_cache[net_weekly] = gross_weekly
        return gross_weekly

    def jobseeker_payment(
        self,
        scenario: Scenario,
        weekly_family_income: Decimal,
    ) -> Decimal:
        child_count = len(scenario.children)
        youngest = min(scenario.children) if scenario.children else 0
        inputs: dict[str, bool | int | Decimal] = {
            "jobseeker_support_applicant_age": 25,
            "jobseeker_support_benefit_commenced_on_or_after_1998_07_01": False,
            "jobseeker_support_dependent_children_count": child_count,
            "jobseeker_support_living_with_parent": False,
            "jobseeker_support_partner_ineligible_due_to_sanction_or_strike": False,
            "jobseeker_support_partner_receives_main_benefit": scenario.partnered,
            "jobseeker_support_partner_receives_new_zealand_superannuation_or_veterans_pension": False,
            "jobseeker_support_single": not scenario.partnered,
            "jobseeker_support_total_income": weekly_family_income,
            "jobseeker_support_transferred_2013_no_dependent_children": False,
            "jobseeker_support_youngest_dependent_child_age": youngest,
        }
        values = self._evaluate(
            entity="Person",
            entity_id=f"{scenario.id}:jobseeker:{decimal_text(weekly_family_income)}",
            inputs=inputs,
            outputs=[JOBSEEKER_OUTPUT],
        )
        return scalar_decimal(values, JOBSEEKER_OUTPUT)

    def sole_parent_payment(
        self,
        scenario: Scenario,
        weekly_family_income: Decimal,
    ) -> Decimal:
        values = self._evaluate(
            entity="Person",
            entity_id=f"{scenario.id}:sole-parent:{decimal_text(weekly_family_income)}",
            inputs={
                "sole_parent_support_personal_earnings_used_for_childcare": D0,
                "sole_parent_support_total_income": weekly_family_income,
            },
            outputs=[SOLE_PARENT_OUTPUT],
        )
        return scalar_decimal(values, SOLE_PARENT_OUTPUT)

    def raw_iwtc_branch(self, scenario: Scenario, weekly_wages: Decimal) -> bool:
        return bool(scenario.children) and weekly_wages >= ORACLE_IWTC_WEEKLY_THRESHOLD

    def benefit_components(
        self,
        scenario: Scenario,
        weekly_wages: Decimal,
    ) -> tuple[Decimal, ...]:
        if scenario.partnered:
            per_person = self.jobseeker_payment(scenario, weekly_wages)
            scheduled = (per_person, per_person)
        elif scenario.children:
            if min(scenario.children) >= 14:
                # Treasury R/emtr.R lines 310-319 deliberately select the
                # lone-parent JSS rate with the SPS income-test scale once the
                # youngest child is 14. RuleSpec's Jobseeker branch encodes
                # that same combination.
                scheduled = (self.jobseeker_payment(scenario, weekly_wages),)
            else:
                scheduled = (self.sole_parent_payment(scenario, weekly_wages),)
        else:
            scheduled = (self.jobseeker_payment(scenario, weekly_wages),)
        if self.raw_iwtc_branch(scenario, weekly_wages):
            return tuple(D0 for _item in scheduled)
        return scheduled

    def zero_income_jobseeker_components(
        self,
        scenario: Scenario,
    ) -> tuple[Decimal, ...]:
        per_person = self.jobseeker_payment(scenario, D0)
        if scenario.partnered:
            return (per_person, per_person)
        return (per_person,)

    def family_scheme_inputs(
        self,
        annual_base_income: Decimal,
        annual_wages: Decimal,
    ) -> dict[str, bool | int | Decimal]:
        inputs: dict[str, bool | int | Decimal] = {
            "family_scheme_base_income_excluding_mb3_to_mb13_adjustments": annual_base_income,
            "family_scheme_activity_income": D0,
            "family_scheme_activity_deductions": D0,
            "family_scheme_superannuation_distribution_income": D0,
            "family_scheme_retirement_scheme_distribution_income": D0,
            "family_scheme_close_company_person_voting_interest": D0,
            "family_scheme_close_company_dependent_child_voting_interest": D0,
            "family_scheme_close_company_relevant_major_shareholders": 0,
            "family_scheme_close_company_net_income": D0,
            "family_scheme_close_company_main_income_equalisation_deposits": D0,
            "family_scheme_close_company_main_income_equalisation_refunds": D0,
            "family_scheme_close_company_dividends": D0,
            "family_scheme_trustee_net_income": D0,
            "family_scheme_trustee_main_income_equalisation_deposits": D0,
            "family_scheme_trustee_main_income_equalisation_refunds": D0,
            "family_scheme_trustee_beneficiary_income_vested_or_paid": D0,
            "family_scheme_trustee_company_voting_interest": D0,
            "family_scheme_trustee_company_net_income": D0,
            "family_scheme_trustee_company_main_income_equalisation_deposits": D0,
            "family_scheme_trustee_company_main_income_equalisation_refunds": D0,
            "family_scheme_trustee_company_dividends": D0,
            "family_scheme_trust_settlors_alive_count": 0,
            "family_scheme_employee_salary_or_wages": annual_wages,
            "family_scheme_short_term_charge_facility_value_excluding_fbt": D0,
            "family_scheme_short_term_charge_facility_value_including_fbt": D0,
            "family_scheme_employment_income_foregone_for_motor_vehicle": D0,
            "family_scheme_controlling_shareholder_voting_interest": D0,
            "family_scheme_attributed_fringe_benefits_taxable_value": D0,
            "family_scheme_attributed_fringe_benefits_fbt_liability": D0,
            "family_scheme_exempt_pension_or_annuity_amount": D0,
            "family_scheme_dependent_child_relevant_amounts": D0,
            "family_scheme_dependent_child_principal_caregivers_count": 0,
            "family_scheme_spouse_or_partner_nonresident_foreign_sourced_income": D0,
            "family_scheme_commissioner_excludes_non_settlor_trust_payment": False,
            "family_scheme_non_settlor_trust_payment": D0,
            "family_scheme_other_payments_not_excluded": D0,
            "family_scheme_income_period_days": 365,
        }
        return inputs

    def iwtc_eligibility_inputs(
        self,
        scenario: Scenario,
        weekly_wages: Decimal,
        net_benefit: Decimal,
    ) -> dict[str, bool | int | Decimal]:
        has_children = bool(scenario.children)
        earns_paye = weekly_wages > 0
        return {
            "wff_commissioner_considers_primary_day_to_day_care": has_children,
            "wff_care_is_temporary": False,
            "wff_caregiver_is_body_of_persons": False,
            "wff_caregiver_is_spouse_or_partner_of_non_electing_transitional_resident": False,
            "wff_caregiver_is_disqualifying_residence_or_institution_operator_or_employee": False,
            "wff_caregiver_lives_apart_from_another_qualifying_person_for_child": has_children,
            "in_work_tax_credit_child_exclusive_care_fraction": D1 if has_children else D0,
            "in_work_tax_credit_person_age": 25,
            "in_work_tax_credit_child_financially_dependent": has_children,
            "in_work_tax_credit_child_treated_financially_dependent_by_payments": False,
            "in_work_tax_credit_person_new_zealand_resident": True,
            "in_work_tax_credit_person_present_in_new_zealand_continuous_months": 12,
            "in_work_tax_credit_person_resident_under_yd1_on_credit_days": True,
            "in_work_tax_credit_person_transitional_resident": False,
            "in_work_tax_credit_person_spouse_or_partner_transitional_resident": False,
            "in_work_tax_credit_child_new_zealand_resident": has_children,
            "in_work_tax_credit_child_present_in_new_zealand_for_entitlement_period": has_children,
            "in_work_tax_credit_person_or_partner_receives_main_benefit": net_benefit > 0,
            "in_work_tax_credit_person_or_partner_receives_basic_and_independent_circumstances_grants": False,
            "in_work_tax_credit_person_or_partner_receives_parent_allowance_or_childrens_pension": False,
            "in_work_tax_credit_allowed_paye_income_payment": earns_paye,
            "in_work_tax_credit_rd3b_or_rd3c_income": False,
            "in_work_tax_credit_business_income_from_profit_activity": False,
            "in_work_tax_credit_personal_service_rehabilitation_payment_income": False,
            "in_work_tax_credit_normally_earner": earns_paye,
            "in_work_tax_credit_earner_in_relation_to_close_company": False,
            "in_work_tax_credit_earner_major_shareholder_in_close_company": False,
            "in_work_tax_credit_close_company_derives_gross_income": False,
            "in_work_tax_credit_child_tax_credit_received_for_period_ending_2006_03_31": False,
            "in_work_tax_credit_incapacity_suffered_between_2006_01_01_and_2006_03_31": False,
            "in_work_tax_credit_weekly_compensation_paid_for_incapacity": False,
            "in_work_tax_credit_full_time_earner_income_at_incapacity": False,
            "in_work_tax_credit_would_have_been_eligible_under_legacy_formula": False,
            "in_work_tax_credit_normally_full_time_earner": False,
            "in_work_tax_credit_birth_absence_weeks": 0,
            "in_work_tax_credit_work_reduced_or_stopped_due_to_child_birth": False,
            "in_work_tax_credit_entitled_to_parental_tax_credit_for_child": False,
            "in_work_tax_credit_currently_meets_fifth_requirement": True,
            "in_work_tax_credit_days_since_last_met_fifth_requirement": 0,
        }

    def family_credit_values(
        self,
        *,
        scenario: Scenario,
        weekly_wages: Decimal,
        weekly_gross_benefits: Decimal,
        net_benefit: Decimal,
        wage_tax_total: Decimal,
        hours_total: Decimal,
    ) -> dict[str, Decimal | str]:
        child_count = len(scenario.children)
        annual_wages = weekly_wages * WEEKS_IN_MODEL_YEAR
        annual_base_income = (
            weekly_wages + weekly_gross_benefits
        ) * WEEKS_IN_MODEL_YEAR
        inputs = self.family_scheme_inputs(annual_base_income, annual_wages)
        inputs.update(
            {
                "family_tax_credit_eldest_dependent_child_care_units": (
                    D1 if child_count else D0
                ),
                "family_tax_credit_subsequent_dependent_child_care_units": Decimal(
                    max(0, child_count - 1)
                ),
                "family_tax_credit_entitlement_days": 365 if child_count else 0,
                "wff_family_credit_abatement_days": 365 if child_count else 0,
                "in_work_tax_credit_allowed_children_count": child_count,
                "in_work_tax_credit_weekly_periods": 52 if child_count else 0,
                "child_tax_credit_for_entitlement_period": D0,
                "parental_tax_credit_for_entitlement_period": D0,
                "parental_tax_credit_additional_abatement": D0,
            }
        )
        inputs.update(
            self.iwtc_eligibility_inputs(scenario, weekly_wages, net_benefit)
        )
        full_time_hours = Decimal(30 if scenario.partnered else 20)
        mftc_eligible = (
            bool(child_count)
            and hours_total >= full_time_hours
            and net_benefit == 0
        )
        inputs.update(
            {
                "minimum_family_scheme_income_attributable_to_full_time_weeks": (
                    weekly_wages * D52 if mftc_eligible else D0
                ),
                "minimum_family_full_time_earner_weeks": 52 if mftc_eligible else 0,
                "minimum_family_adjusted_income_tax_liability": (
                    wage_tax_total * D52 if mftc_eligible else D0
                ),
                "minimum_family_amount_received": D0,
                "minimum_family_amount_paid": D0,
                "minimum_family_tax_credit_weekly_periods": (
                    52 if mftc_eligible else 0
                ),
            }
        )
        return self._evaluate(
            entity="Family",
            entity_id=f"{scenario.id}:family:{decimal_text(weekly_wages)}",
            inputs=inputs,
            outputs=[
                FTC_OUTPUT,
                IWTC_BEFORE_OUTPUT,
                IWTC_REMAINING_ABATEMENT_OUTPUT,
                IWTC_ENTITLEMENT_OUTPUT,
                MFTC_OUTPUT,
                FSI_OUTPUT,
            ],
        )

    def best_start_total(
        self,
        *,
        scenario: Scenario,
        annual_base_income: Decimal,
        annual_wages: Decimal,
    ) -> tuple[Decimal, Decimal]:
        eligible_children = [
            index for index, age in enumerate(scenario.children) if age in (0, 1, 2)
        ]
        total_before_abatement = D0
        per_child_total = D0
        family_abatement: Decimal | None = None
        for index in eligible_children:
            inputs = self.family_scheme_inputs(annual_base_income, annual_wages)
            inputs.update(
                {
                    "best_start_entitlement_days": 365,
                    "best_start_child_care_fraction": D1,
                    "best_start_abatement_days": 365,
                }
            )
            values = self._evaluate(
                entity="Child",
                entity_id=f"{scenario.id}:child:{index}",
                inputs=inputs,
                outputs=[
                    BEST_START_BEFORE_OUTPUT,
                    BEST_START_ABATEMENT_OUTPUT,
                    BEST_START_OUTPUT,
                ],
            )
            child_before = scalar_decimal(values, BEST_START_BEFORE_OUTPUT)
            child_abatement = scalar_decimal(
                values, BEST_START_ABATEMENT_OUTPUT
            )
            total_before_abatement += child_before
            per_child_total += scalar_decimal(values, BEST_START_OUTPUT)
            if family_abatement is None:
                family_abatement = child_abatement
            elif child_abatement != family_abatement:
                raise HarnessError(
                    "Best Start family abatement changed between children for "
                    f"{scenario.id}"
                )
        aggregate_total = max(
            D0,
            total_before_abatement - (family_abatement or D0),
        )
        return (
            aggregate_total / WEEKS_IN_MODEL_YEAR,
            per_child_total / WEEKS_IN_MODEL_YEAR,
        )

    def ietc_for_person(
        self,
        *,
        scenario: Scenario,
        person: int,
        weekly_wage: Decimal,
        weekly_benefit: Decimal,
        family_support_payable: bool,
    ) -> Decimal:
        primary = person == 1
        inputs: dict[str, bool | int | Decimal] = {
            "independent_earner_tax_credit_net_income": (
                weekly_wage * WEEKS_IN_MODEL_YEAR
            ),
            "independent_earner_tax_credit_period_whole_months": 12,
            "independent_earner_tax_credit_person_is_natural_person": True,
            "independent_earner_tax_credit_resident_in_new_zealand": True,
            "independent_earner_tax_credit_receives_main_benefit": (
                weekly_benefit > 0
            ),
            "independent_earner_tax_credit_receives_veterans_pension": False,
            "independent_earner_tax_credit_receives_new_zealand_superannuation": False,
            "independent_earner_tax_credit_entitled_to_or_receives_wff_tax_credit": (
                family_support_payable if primary else False
            ),
            "independent_earner_tax_credit_partner_entitled_to_and_receives_wff_tax_credit": (
                family_support_payable if not primary else False
            ),
            "independent_earner_tax_credit_receives_overseas_like_support": False,
            "independent_earner_tax_credit_partner_receives_overseas_like_wff_tax_credit": False,
        }
        values = self._evaluate(
            entity="Person",
            entity_id=(
                f"{scenario.id}:p{person}:ietc:{decimal_text(weekly_wage)}"
            ),
            inputs=inputs,
            outputs=[IETC_OUTPUT],
        )
        return scalar_decimal(values, IETC_OUTPUT) / WEEKS_IN_MODEL_YEAR

    def winter_energy_average(
        self,
        scenario: Scenario,
        net_benefit: Decimal,
    ) -> Decimal:
        if net_benefit <= 0:
            return D0
        values = self._evaluate(
            entity="Person",
            entity_id=f"{scenario.id}:winter-energy-rate",
            inputs={
                "winter_energy_payment_single": not scenario.partnered,
                "winter_energy_payment_has_dependent_children": bool(
                    scenario.children
                ),
            },
            outputs=[WEP_RATE_OUTPUT],
        )
        return scalar_decimal(values, WEP_RATE_OUTPUT) / WEEKS_IN_MODEL_YEAR

    def accommodation_cutout(
        self,
        scenario: Scenario,
        *,
        treasury_host_aligned: bool,
    ) -> Decimal:
        key = (
            scenario.partnered,
            len(scenario.children),
            treasury_host_aligned,
        )
        if key in self._as_cutout_cache:
            return self._as_cutout_cache[key]
        if not scenario.partnered and scenario.children:
            # Treasury's source-defined lone-parent AS branch is deliberately
            # not the SPS/JSS-with-children benefit schedule used for current
            # net benefit. R/emtr.R lines 324-329 instead combine the lone-
            # parent JSS base rate with the JSS (Income Test 3) 70% scale.
            raw_cutout = (
                self.benefit_income_test_lower_threshold
                + self.jobseeker_single_with_children_rate
                / self.benefit_income_test_3_rate
            )
        else:
            anchor = Decimal(500)
            at_anchor = self.jobseeker_payment(scenario, anchor)
            after_one_dollar = self.jobseeker_payment(scenario, anchor + D1)
            reduction_per_dollar = at_anchor - after_one_dollar
            if at_anchor <= 0 or reduction_per_dollar <= 0:
                raise HarnessError(
                    "could not derive Accommodation Supplement cutout from the "
                    f"Jobseeker schedule for {scenario.id}"
                )
            raw_cutout = anchor + at_anchor / reduction_per_dollar
        if treasury_host_aligned:
            # Raw IncomeExplorer imposes this annual-dollar ceiling. Regulation
            # 18 instead asks for the exact income level that extinguishes JSS.
            annual_ceiling = (
                raw_cutout * WEEKS_IN_MODEL_YEAR
            ).to_integral_value(rounding=ROUND_CEILING)
            cutout = annual_ceiling / WEEKS_IN_MODEL_YEAR
        else:
            cutout = raw_cutout
        self._as_cutout_cache[key] = cutout
        return cutout

    def accommodation_values(
        self,
        *,
        scenario: Scenario,
        weekly_wages: Decimal,
        net_benefit: Decimal,
        eldest_ftc_annual: Decimal,
        treasury_host_aligned: bool,
    ) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        zero_income_benefit = sum(
            self.zero_income_jobseeker_components(scenario), D0
        )
        base_rate = zero_income_benefit
        if scenario.children:
            # Social Security Regulations 2018 reg 17 uses the annual FTC rate
            # divided by 52. Treasury raw emtr() instead divides by 365/7; that
            # source-host convention is retained only in the labeled diagnostic.
            base_rate += eldest_ftc_annual / (
                WEEKS_IN_MODEL_YEAR if treasury_host_aligned else D52
            )
        cutout = self.accommodation_cutout(
            scenario,
            treasury_host_aligned=treasury_host_aligned,
        )
        rent = scenario.accommodation_rent
        boarder = scenario.accommodation_boarder
        area = scenario.accommodation_area
        inputs: dict[str, bool | int | Decimal] = {
            "accommodation_supplement_additional_resident_in_social_housing": False,
            "accommodation_supplement_area_let_to_nonresidents": D0,
            "accommodation_supplement_base_rate_weekly_amount": base_rate,
            "accommodation_supplement_boarder": boarder,
            "accommodation_supplement_business_use_area": D0,
            "accommodation_supplement_costs_are_homeownership": not rent,
            "accommodation_supplement_has_dependent_children": bool(
                scenario.children
            ),
            "accommodation_supplement_has_two_or_more_dependent_children": (
                len(scenario.children) >= 2
            ),
            "accommodation_supplement_in_relationship": scenario.partnered,
            "accommodation_supplement_joint_owner_with_resident": False,
            "accommodation_supplement_non_beneficiary": net_benefit == 0,
            "accommodation_supplement_non_beneficiary_income_cutout_weekly_amount": (
                cutout
            ),
            "accommodation_supplement_owner_weekly_payment_share": D0,
            "accommodation_supplement_owner_weekly_required_payments": (
                scenario.accommodation_costs
                if not rent and not boarder
                else D0
            ),
            "accommodation_supplement_owns_premises_and_not_joint_owner_with_resident": (
                not rent and not boarder
            ),
            "accommodation_supplement_relevant_weekly_income": weekly_wages,
            "accommodation_supplement_resides_in_area_1": area == 1,
            "accommodation_supplement_resides_in_area_2": area == 2,
            "accommodation_supplement_resides_in_area_3": area == 3,
            "accommodation_supplement_self_contained_area_let_to_residents": D0,
            "accommodation_supplement_social_housing_weekly_contributions_paid": D0,
            "accommodation_supplement_sole_parent": (
                not scenario.partnered and bool(scenario.children)
            ),
            "accommodation_supplement_total_premises_area": D0,
            "accommodation_supplement_weekly_board_and_lodgings_paid": (
                scenario.weekly_board_and_lodgings_paid
            ),
            "accommodation_supplement_weekly_boarder_payments_received": D0,
            "accommodation_supplement_weekly_contributions_received_from_additional_residents": D0,
            "accommodation_supplement_weekly_rent_paid": (
                scenario.accommodation_costs if rent and not boarder else D0
            ),
            "accommodation_supplement_weekly_rent_received_from_other_residents": D0,
        }
        values = self._evaluate(
            entity="Family",
            entity_id=(
                f"{scenario.id}:as:"
                f"{'treasury-host' if treasury_host_aligned else 'statutory'}:"
                f"{decimal_text(weekly_wages)}"
            ),
            inputs=inputs,
            outputs=[AS_UNROUNDED_OUTPUT, AS_ROUNDED_OUTPUT],
        )
        return (
            scalar_decimal(values, AS_UNROUNDED_OUTPUT),
            scalar_decimal(values, AS_ROUNDED_OUTPUT),
            base_rate,
            cutout,
        )

    def evaluate_state(
        self,
        scenario: Scenario,
        weekly_wage1: Decimal,
    ) -> dict[str, Decimal | str]:
        weekly_wage2 = scenario.gross_wage2
        weekly_wages = weekly_wage1 + weekly_wage2
        hours1 = (
            weekly_wage1 / scenario.wage1_hourly
            if scenario.wage1_hourly > 0
            else D0
        )
        hours_total = hours1 + scenario.hours2
        benefit_components = self.benefit_components(scenario, weekly_wages)
        net_benefit = sum(benefit_components, D0)
        gross_benefits = tuple(
            self.gross_benefit_from_net_weekly(value)
            for value in benefit_components
        )
        gross_benefit_total = sum(gross_benefits, D0)

        primary_gross_benefit = gross_benefits[0]
        tax1 = (
            self.annual_tax(
                (primary_gross_benefit + weekly_wage1) * WEEKS_IN_MODEL_YEAR
            )
            - self.annual_tax(primary_gross_benefit * WEEKS_IN_MODEL_YEAR)
        ) / WEEKS_IN_MODEL_YEAR
        acc1 = self.annual_acc(
            weekly_wage1 * WEEKS_IN_MODEL_YEAR
        ) / WEEKS_IN_MODEL_YEAR
        net_wage1 = weekly_wage1 - tax1 - acc1

        tax2 = D0
        acc2 = D0
        net_wage2 = D0
        if scenario.partnered:
            partner_gross_benefit = gross_benefits[1]
            tax2 = (
                self.annual_tax(
                    (partner_gross_benefit + weekly_wage2)
                    * WEEKS_IN_MODEL_YEAR
                )
                - self.annual_tax(partner_gross_benefit * WEEKS_IN_MODEL_YEAR)
            ) / WEEKS_IN_MODEL_YEAR
            acc2 = self.annual_acc(
                weekly_wage2 * WEEKS_IN_MODEL_YEAR
            ) / WEEKS_IN_MODEL_YEAR
            net_wage2 = weekly_wage2 - tax2 - acc2
        net_wage = net_wage1 + net_wage2

        family_values = self.family_credit_values(
            scenario=scenario,
            weekly_wages=weekly_wages,
            weekly_gross_benefits=gross_benefit_total,
            net_benefit=net_benefit,
            wage_tax_total=tax1 + tax2,
            hours_total=hours_total,
        )
        ftc = scalar_decimal(family_values, FTC_OUTPUT) / WEEKS_IN_MODEL_YEAR
        iwtc_before = scalar_decimal(family_values, IWTC_BEFORE_OUTPUT) / D52
        iwtc_remaining_abatement = (
            scalar_decimal(family_values, IWTC_REMAINING_ABATEMENT_OUTPUT)
            / WEEKS_IN_MODEL_YEAR
        )
        iwtc = max(D0, iwtc_before - iwtc_remaining_abatement)
        mftc = scalar_decimal(family_values, MFTC_OUTPUT) / D52
        wff = ftc + iwtc

        annual_wages = weekly_wages * WEEKS_IN_MODEL_YEAR
        annual_base_income = (
            weekly_wages + gross_benefit_total
        ) * WEEKS_IN_MODEL_YEAR
        best_start, best_start_per_child = self.best_start_total(
            scenario=scenario,
            annual_base_income=annual_base_income,
            annual_wages=annual_wages,
        )
        family_support_payable = (wff + mftc + best_start) > 0
        ietc1 = self.ietc_for_person(
            scenario=scenario,
            person=1,
            weekly_wage=weekly_wage1,
            weekly_benefit=benefit_components[0],
            family_support_payable=family_support_payable,
        )
        ietc2 = D0
        if scenario.partnered:
            ietc2 = self.ietc_for_person(
                scenario=scenario,
                person=2,
                weekly_wage=weekly_wage2,
                weekly_benefit=benefit_components[1],
                family_support_payable=family_support_payable,
            )
        ietc = ietc1 + ietc2
        winter_energy = self.winter_energy_average(scenario, net_benefit)
        (
            as_unrounded,
            as_rounded,
            as_base_rate,
            as_cutout,
        ) = self.accommodation_values(
            scenario=scenario,
            weekly_wages=weekly_wages,
            net_benefit=net_benefit,
            eldest_ftc_annual=self.ftc_eldest_annual,
            treasury_host_aligned=False,
        )
        (
            as_treasury_host_aligned,
            _as_treasury_host_aligned_rounded,
            as_treasury_host_base_rate,
            as_treasury_host_cutout,
        ) = self.accommodation_values(
            scenario=scenario,
            weekly_wages=weekly_wages,
            net_benefit=net_benefit,
            eldest_ftc_annual=self.ftc_eldest_annual,
            treasury_host_aligned=True,
        )
        net_income = (
            net_wage
            + net_benefit
            + wff
            + mftc
            + ietc
            + winter_energy
            + best_start
            + as_unrounded
        )
        return {
            "gross_wage1": weekly_wage1,
            "hours1": hours1,
            "gross_wage1_annual": weekly_wage1 * WEEKS_IN_MODEL_YEAR,
            "gross_wage2": weekly_wage2,
            "wage1_tax": tax1,
            "wage1_ACC_levy": acc1,
            "net_wage1": net_wage1,
            "net_wage": net_wage,
            "net_benefit": net_benefit,
            "FTC_abated": ftc,
            "IWTC_abated": iwtc,
            "MFTC": mftc,
            "IETC_abated": ietc,
            "WinterEnergy": winter_energy,
            "BestStart_Total": best_start,
            "BestStart_Total_naive_per_child_abatement": (
                best_start_per_child
            ),
            "AS_Amount": as_unrounded,
            "WFF_abated": wff,
            "Net_Income": net_income,
            "Net_Income_annual": net_income * WEEKS_IN_MODEL_YEAR,
            "AS_Amount_statutory_rounded": as_rounded,
            "AS_Amount_treasury_host_aligned": as_treasury_host_aligned,
            "AS_statutory_base_rate": as_base_rate,
            "AS_treasury_host_base_rate": as_treasury_host_base_rate,
            "AS_statutory_cutout": as_cutout,
            "AS_treasury_host_cutout": as_treasury_host_cutout,
            "gross_benefit_taxable_weekly": gross_benefit_total,
            "wage2_tax": tax2,
            "wage2_ACC_levy": acc2,
            "net_wage2": net_wage2,
            "family_scheme_income": scalar_decimal(family_values, FSI_OUTPUT),
            "iwtc_entitlement": str(
                family_values[IWTC_ENTITLEMENT_OUTPUT]
            ),
        }


def sweep_scenario(
    evaluator: ModelEvaluator,
    scenario: Scenario,
) -> dict[int, dict[str, Decimal | str | None]]:
    required_wages = set(scenario.sampled_wages)
    if 1500 in required_wages:
        required_wages.add(1499)
    required_wages.update(
        wage + 1 for wage in scenario.sampled_wages if wage < 1500
    )
    states = {
        wage: evaluator.evaluate_state(scenario, Decimal(wage))
        for wage in sorted(required_wages)
    }
    baseline = scalar_decimal(states[0], "Net_Income")
    sampled: dict[int, dict[str, Decimal | str | None]] = {}
    for wage in scenario.sampled_wages:
        state: dict[str, Decimal | str | None] = dict(states[wage])
        if wage == 1500:
            current_state = states[1499]
            following_state = states[1500]
        else:
            current_state = states[wage]
            following_state = states[wage + 1]
        current = scalar_decimal(current_state, "Net_Income")
        following = scalar_decimal(following_state, "Net_Income")
        state["EMTR"] = D1 - (following - current)
        rulespec_acc_marginal = (
            scalar_decimal(following_state, "wage1_ACC_levy")
            - scalar_decimal(current_state, "wage1_ACC_levy")
        )
        state["EMTR_ACC_rounding_component"] = (
            rulespec_acc_marginal - ORACLE_ACC_WEEKLY_RATE
        )
        current_wff = scalar_decimal(current_state, "WFF_abated")
        following_wff = scalar_decimal(following_state, "WFF_abated")
        continuous_wff_marginal_loss = (
            evaluator.wff_abatement_rate
            if (
                scalar_decimal(current_state, "family_scheme_income")
                > evaluator.wff_abatement_threshold
                and current_wff > 0
                and following_wff > 0
            )
            else D0
        )
        state["EMTR_WFF_complete_dollar_component"] = (
            current_wff
            - following_wff
            - continuous_wff_marginal_loss
        )
        net_income = scalar_decimal(state, "Net_Income")
        state["RR"] = baseline / net_income if net_income != 0 else None
        gross_income = Decimal(wage) + scenario.gross_wage2
        state["PTR"] = (
            D1 - (net_income - baseline) / gross_income
            if gross_income != 0
            else None
        )
        sampled[wage] = state
    return sampled


@dataclass(frozen=True)
class ComparisonRow:
    scenario_id: str
    scenario_description: str
    weekly_wage: int
    column: str
    unit: str
    treasury: Decimal
    rulespec: Decimal
    signed_delta: Decimal
    absolute_delta: Decimal
    relative_delta: Decimal | None
    classification: str
    reason_code: str


CLASSIFICATION_DETAILS: dict[str, tuple[str, str, str]] = {
    "MATCH_SNAPSHOT_PRECISION": (
        "match",
        "Match at oracle precision",
        "The absolute difference is at most half of the snapshot's six-decimal "
        "rounding unit.",
    ),
    "A_SCENARIO_ENCODING": (
        "a",
        "Scenario encoding bug",
        "A direct scenario identity (wage, hours, or annualisation) did not "
        "survive the host-to-engine mapping.",
    ),
    "B_BENEFIT_VINTAGE": (
        "b",
        "Main-benefit forecast vintage",
        "Treasury's BEFU25 TY27 rate differs from the enacted 1 April 2026 "
        "rate under Social Security Act 2018 Schedule 4 as amended by the "
        "Social Security (Rates of Benefits and Allowances) Order 2026 cl 5.",
    ),
    "B_BENEFIT_GROSSUP_TAX": (
        "b",
        "Benefit-vintage tax interaction",
        "Treasury taxes wages incrementally above its forecast-vintage grossed "
        "benefit. The enacted benefit rate changes that tax base before the "
        "same Schedule 1 tax rates are applied.",
    ),
    "B_WFF_VINTAGE": (
        "b",
        "Working for Families forecast vintage",
        "The BEFU25 FTC, IWTC, MFTC, or Best Start prescribed amount differs "
        "from the amount enacted for 2026/27 under Income Tax Act 2007 "
        "ss MD 3, MD 10, ME 1, or MG 2.",
    ),
    "B_AS_UPSTREAM_VINTAGE": (
        "b",
        "Accommodation Supplement compound difference, primary vintage",
        "A Treasury-host-aligned diagnostic establishes a BEFU25-versus-enacted "
        "benefit/FTC effect. The statutory primary also retains smaller reg "
        "17–18 host conventions: FTC divided by 52 and the exact JSS cutout.",
    ),
    "B_COMPOUND_NET_INCOME": (
        "b",
        "Compound forecast-vintage level difference",
        "At least one material component of net income is a class-(b) benefit "
        "or tax-credit vintage difference; smaller class-(c) rounding effects "
        "may also be present.",
    ),
    "C_ACC_ANNUAL_CENTS": (
        "c",
        "ACC period/rounding convention",
        "Treasury applies an unrounded weekly 1.75% levy. RuleSpec applies the "
        "annual including-GST levy and its whole-cent rounding, then converts "
        "the result by 365/7 weeks.",
    ),
    "C_NET_WAGE_ROUNDING": (
        "c",
        "Net-wage rounding propagation",
        "The net-wage residual is the propagation of annual-cent ACC rounding "
        "through a weekly value (and, for partner wages, the same conversion).",
    ),
    "C_COMPOUND_NET_INCOME": (
        "c",
        "Compound period/rounding difference",
        "No established forecast-vintage component is active; the aggregate "
        "difference is inherited from documented statutory period or rounding "
        "conventions.",
    ),
    "C_IETC_WHOLE_DOLLARS": (
        "c",
        "IETC statutory whole-dollar convention",
        "RuleSpec retains the annual statutory whole-dollar calculation before "
        "converting by 365/7; Treasury's R flow is continuous weekly arithmetic.",
    ),
    "C_AS_STATUTORY_HOST": (
        "c",
        "Accommodation Supplement statutory host convention",
        "The statutory primary uses the reg 17 annual FTC amount divided by 52 "
        "and reg 18's exact JSS vanishing point; raw Treasury uses 365/7 and an "
        "annual-dollar-ceiled cutout.",
    ),
    "C_EMTR_DISCRETE_ROUNDING": (
        "c",
        "EMTR discrete rounding convention",
        "Both sides use the same weekly $1 forward interval. The residual is "
        "caused by RuleSpec's annual-cent ACC rounding and, where applicable, "
        "the complete-dollar WFF abatement base before conversion back to a "
        "week, with any remaining amount bounded by the oracle's six-decimal "
        "display envelope.",
    ),
    "D_UNEXPLAINED": (
        "d",
        "Unexplained",
        "The observed difference is not established by the pinned-vintage or "
        "unit/period evidence in this audit.",
    ),
}


def comparison_unit(column: str) -> str:
    if column == "hours1":
        return "hours/week"
    if column == "gross_wage1_annual" or column == "Net_Income_annual":
        return "NZD/year"
    if column == "EMTR":
        return "ratio"
    return "NZD/week"


def outside_oracle_precision(left: Decimal, right: Decimal) -> bool:
    return abs(left - right) > ORACLE_SIX_DECIMAL_TOLERANCE


def classify_discrepancy(
    *,
    column: str,
    treasury_state: Mapping[str, Any],
    rulespec_state: Mapping[str, Decimal | str | None],
    signed_delta: Decimal,
    absolute_delta: Decimal,
) -> tuple[str, str]:
    if absolute_delta <= ORACLE_SIX_DECIMAL_TOLERANCE:
        return "match", "MATCH_SNAPSHOT_PRECISION"

    if column in {
        "gross_wage1",
        "hours1",
        "gross_wage1_annual",
        "gross_wage2",
    }:
        return "a", "A_SCENARIO_ENCODING"

    treasury_benefit = dec(treasury_state["net_benefit"])
    rulespec_benefit = scalar_decimal(rulespec_state, "net_benefit")
    benefit_vintage_active = (
        treasury_benefit > 0
        or rulespec_benefit > 0
    ) and outside_oracle_precision(treasury_benefit, rulespec_benefit)

    if column == "wage1_tax":
        if benefit_vintage_active:
            return "b", "B_BENEFIT_GROSSUP_TAX"
        return "d", "D_UNEXPLAINED"
    if column == "wage1_ACC_levy":
        return "c", "C_ACC_ANNUAL_CENTS"
    if column in {"net_wage1", "net_wage"}:
        treasury_tax = dec(treasury_state["wage1_tax"])
        rulespec_tax = scalar_decimal(rulespec_state, "wage1_tax")
        if (
            benefit_vintage_active
            and outside_oracle_precision(treasury_tax, rulespec_tax)
        ):
            return "b", "B_BENEFIT_GROSSUP_TAX"
        return "c", "C_NET_WAGE_ROUNDING"
    if column == "net_benefit":
        return "b", "B_BENEFIT_VINTAGE"
    if column in {
        "FTC_abated",
        "IWTC_abated",
        "MFTC",
        "BestStart_Total",
        "WFF_abated",
    }:
        return "b", "B_WFF_VINTAGE"
    if column == "IETC_abated":
        return "c", "C_IETC_WHOLE_DOLLARS"
    if column == "AS_Amount":
        treasury_as = dec(treasury_state["AS_Amount"])
        aligned_as = scalar_decimal(
            rulespec_state, "AS_Amount_treasury_host_aligned"
        )
        if outside_oracle_precision(treasury_as, aligned_as):
            return "b", "B_AS_UPSTREAM_VINTAGE"
        if outside_oracle_precision(
            aligned_as,
            scalar_decimal(rulespec_state, "AS_Amount"),
        ):
            return "c", "C_AS_STATUTORY_HOST"
        return "d", "D_UNEXPLAINED"
    if column in {"Net_Income", "Net_Income_annual"}:
        material_vintage_columns = (
            "wage1_tax",
            "net_benefit",
            "FTC_abated",
            "IWTC_abated",
            "MFTC",
            "BestStart_Total",
            "AS_Amount",
        )
        material_vintage_difference = False
        for name in material_vintage_columns:
            component_differs = outside_oracle_precision(
                dec(treasury_state[name]),
                scalar_decimal(rulespec_state, name),
            )
            if not component_differs:
                continue
            if name == "wage1_tax" and not benefit_vintage_active:
                continue
            if name == "AS_Amount" and not outside_oracle_precision(
                dec(treasury_state["AS_Amount"]),
                scalar_decimal(
                    rulespec_state,
                    "AS_Amount_treasury_host_aligned",
                ),
            ):
                continue
            material_vintage_difference = True
            break
        if material_vintage_difference:
            return "b", "B_COMPOUND_NET_INCOME"
        return "c", "C_COMPOUND_NET_INCOME"
    if column == "EMTR":
        explained = (
            scalar_decimal(
                rulespec_state, "EMTR_ACC_rounding_component"
            )
            + scalar_decimal(
                rulespec_state,
                "EMTR_WFF_complete_dollar_component",
            )
        )
        if abs(signed_delta - explained) <= ORACLE_SIX_DECIMAL_TOLERANCE:
            return "c", "C_EMTR_DISCRETE_ROUNDING"
        return "d", "D_UNEXPLAINED"
    return "d", "D_UNEXPLAINED"


def build_comparison_rows(
    *,
    oracle: Mapping[str, Any],
    scenarios: Sequence[Scenario],
    sweeps: Mapping[str, Mapping[int, Mapping[str, Decimal | str | None]]],
) -> list[ComparisonRow]:
    oracle_by_id = {str(item["id"]): item for item in oracle["scenarios"]}
    rows: list[ComparisonRow] = []
    for scenario in scenarios:
        raw_scenario = oracle_by_id[scenario.id]
        sampled_outputs = raw_scenario["sampled_outputs"]
        if len(sampled_outputs) != len(scenario.sampled_wages):
            raise HarnessError(
                f"{scenario.id} has {len(sampled_outputs)} oracle points"
            )
        for index, wage in enumerate(scenario.sampled_wages):
            treasury_state = sampled_outputs[index]
            if dec(treasury_state["gross_wage1"]) != Decimal(wage):
                raise HarnessError(
                    f"{scenario.id} oracle row {index} is not wage {wage}"
                )
            rulespec_state = sweeps[scenario.id][wage]
            for column in COMPARISON_COLUMNS:
                treasury_value = dec(treasury_state[column])
                rulespec_value = scalar_decimal(rulespec_state, column)
                signed_delta = rulespec_value - treasury_value
                absolute_delta = abs(signed_delta)
                if treasury_value != 0:
                    relative_delta = absolute_delta / abs(treasury_value)
                elif absolute_delta == 0:
                    relative_delta = D0
                else:
                    relative_delta = None
                classification, reason_code = classify_discrepancy(
                    column=column,
                    treasury_state=treasury_state,
                    rulespec_state=rulespec_state,
                    signed_delta=signed_delta,
                    absolute_delta=absolute_delta,
                )
                expected_class = CLASSIFICATION_DETAILS[reason_code][0]
                if classification != expected_class:
                    raise HarnessError(
                        f"classification metadata mismatch for {reason_code}"
                    )
                rows.append(
                    ComparisonRow(
                        scenario_id=scenario.id,
                        scenario_description=scenario.description,
                        weekly_wage=wage,
                        column=column,
                        unit=comparison_unit(column),
                        treasury=treasury_value,
                        rulespec=rulespec_value,
                        signed_delta=signed_delta,
                        absolute_delta=absolute_delta,
                        relative_delta=relative_delta,
                        classification=classification,
                        reason_code=reason_code,
                    )
                )
    return rows


@dataclass(frozen=True)
class VintageParameter:
    label: str
    treasury_name: str
    treasury_value: Decimal
    rulespec_name: str
    unit: str
    statute: str
    corpus_citation_path: str


VINTAGE_PARAMETERS = (
    VintageParameter(
        label="Sole Parent Support / lone-parent JSS",
        treasury_name="Benefits_SPS_Rate",
        treasury_value=Decimal("517.39"),
        rulespec_name="sole_parent_support_weekly_rate",
        unit="NZD/week",
        statute=(
            "Social Security Act 2018 Sch 4 pt 2 cl 1 (SPS) and pt 1 "
            "cl 1(f) (lone-parent JSS); Social Security (Rates of Benefits "
            "and Allowances) Order 2026 cl 5"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2018/0032/schedule/4/part/2/clause/lms118467; "
            "nz/statute/act/public/2018/0032/schedule/4/part/1/clause/lms118447"
        ),
    ),
    VintageParameter(
        label="JSS partnered with children, each adult",
        treasury_name="Benefits_JSS_Rate_CoupleParent",
        treasury_value=Decimal("332.05"),
        rulespec_name=(
            "jobseeker_support_partnered_both_main_benefits_with_children_weekly_rate"
        ),
        unit="NZD/week",
        statute=(
            "Social Security Act 2018 Sch 4 pt 1 cl 1(g)(ii); Social "
            "Security (Rates of Benefits and Allowances) Order 2026 cl 5"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2018/0032/schedule/4/part/1/clause/lms118447"
        ),
    ),
    VintageParameter(
        label="JSS single, no children",
        treasury_name="Benefits_JSS_Rate_Single",
        treasury_value=Decimal("369.60"),
        rulespec_name="jobseeker_support_single_no_children_standard_weekly_rate",
        unit="NZD/week",
        statute=(
            "Social Security Act 2018 Sch 4 pt 1 cl 1(d); Social Security "
            "(Rates of Benefits and Allowances) Order 2026 cl 5"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2018/0032/schedule/4/part/1/clause/lms118447"
        ),
    ),
    VintageParameter(
        label="Family Tax Credit, eldest child",
        treasury_name="FamilyAssistance_FTC_Rates_FirstChild",
        treasury_value=Decimal("7524"),
        rulespec_name="family_tax_credit_eldest_child_annual_amount",
        unit="NZD/year",
        statute=(
            "Income Tax Act 2007 s MD 3(4)(a); Income Tax (Tax Credit) "
            "Order 2025 cl 4"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2007/0097/section/md-3"
        ),
    ),
    VintageParameter(
        label="Family Tax Credit, subsequent child",
        treasury_name="FamilyAssistance_FTC_Rates_SubsequentChild",
        treasury_value=Decimal("6130"),
        rulespec_name="family_tax_credit_subsequent_child_annual_amount",
        unit="NZD/year",
        statute=(
            "Income Tax Act 2007 s MD 3(4)(b); Income Tax (Tax Credit) "
            "Order 2025 cl 4"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2007/0097/section/md-3"
        ),
    ),
    VintageParameter(
        label="In-Work Tax Credit, base",
        treasury_name="FamilyAssistance_IWTC_Rates_UpTo3Children",
        treasury_value=Decimal("5070"),
        rulespec_name="in_work_tax_credit_base_annual_amount",
        unit="NZD/year",
        statute=(
            "Income Tax Act 2007 s MD 10(3)(a); Taxation (Annual Rates for "
            "2025-26, Compliance Simplification, and Remedial Measures) "
            "Act 2026 ss 2, 105"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2026/0008/section/105"
        ),
    ),
    VintageParameter(
        label="Minimum Family Tax Credit prescribed amount",
        treasury_name="FamilyAssistance_MFTC_Rates_MinimumIncome",
        treasury_value=Decimal("36504"),
        rulespec_name="minimum_family_tax_credit_prescribed_amount",
        unit="NZD/year",
        statute=(
            "Income Tax Act 2007 s ME 1(3)(a); Income Tax (Tax Credit) "
            "Order 2025 cl 5"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2007/0097/section/me-1"
        ),
    ),
    VintageParameter(
        label="Best Start prescribed amount, each eligible child",
        treasury_name="FamilyAssistance_BestStart_Rates_Age0",
        treasury_value=Decimal("3838"),
        rulespec_name="best_start_tax_credit_prescribed_amount",
        unit="NZD/year",
        statute=(
            "Income Tax Act 2007 s MG 2(2)(a); Income Tax (Tax Credit) "
            "Order 2025 cl 6"
        ),
        corpus_citation_path=(
            "nz/statute/act/public/2007/0097/section/mg-2"
        ),
    ),
)


def read_top_level_yaml_decimal(path: Path, name: str) -> Decimal:
    prefix = f"{name}:"
    with path.open(encoding="utf-8") as source:
        for raw_line in source:
            if raw_line.startswith(prefix):
                value = raw_line[len(prefix) :].strip()
                try:
                    return Decimal(value)
                except Exception as exc:
                    raise HarnessError(
                        f"Treasury YAML value {name!r} is not a scalar decimal"
                    ) from exc
    raise HarnessError(f"Treasury YAML has no top-level parameter {name!r}")


def build_vintage_parameter_rows(
    compiled: Mapping[str, Any],
    provenance: Provenance,
) -> list[dict[str, Any]]:
    parameter_path = provenance.treasury_root / EXPECTED_PARAMETER_FILE
    if provenance.treasury_present:
        treasury_jss_sole_parent = read_top_level_yaml_decimal(
            parameter_path, "Benefits_JSS_Rate_SoleParent"
        )
        if treasury_jss_sole_parent != Decimal("517.39"):
            raise HarnessError(
                "pinned Treasury Benefits_JSS_Rate_SoleParent changed: "
                f"{decimal_text(treasury_jss_sole_parent)}"
            )
    rows: list[dict[str, Any]] = []
    for spec in VINTAGE_PARAMETERS:
        if provenance.treasury_present:
            observed_treasury = read_top_level_yaml_decimal(
                parameter_path, spec.treasury_name
            )
            if observed_treasury != spec.treasury_value:
                raise HarnessError(
                    f"pinned Treasury {spec.treasury_name} changed: expected "
                    f"{decimal_text(spec.treasury_value)}, found "
                    f"{decimal_text(observed_treasury)}"
                )
        rulespec_values = selected_parameter_values(
            compiled, spec.rulespec_name
        )
        if set(rulespec_values) != {0}:
            raise HarnessError(
                f"expected scalar RuleSpec parameter {spec.rulespec_name}"
            )
        rulespec_value = rulespec_values[0]
        rows.append(
            {
                "label": spec.label,
                "treasury_parameter": spec.treasury_name,
                "treasury_befu25": spec.treasury_value,
                "rulespec_parameter": spec.rulespec_name,
                "rulespec_enacted": rulespec_value,
                "signed_delta": rulespec_value - spec.treasury_value,
                "unit": spec.unit,
                "statute": spec.statute,
                "corpus_citation_path": spec.corpus_citation_path,
            }
        )
    return rows


def summary_statistics(rows: Sequence[ComparisonRow]) -> dict[str, Any]:
    class_counts = Counter(row.classification for row in rows)
    reason_counts = Counter(row.reason_code for row in rows)
    net_income_rows = [row for row in rows if row.column == "Net_Income"]
    emtr_rows = [row for row in rows if row.column == "EMTR"]
    dollar_rows = [
        row
        for row in rows
        if row.column not in {"hours1", "EMTR"}
    ]
    if not net_income_rows or len(net_income_rows) != len(emtr_rows):
        raise HarnessError(
            "comparison summary has inconsistent Net Income and EMTR rows"
        )
    dollar_outside_cent = [
        row for row in dollar_rows if row.absolute_delta >= Decimal("0.005")
    ]
    dollar_outside_cent_classes = Counter(
        row.classification for row in dollar_outside_cent
    )
    maximum_net = max(
        net_income_rows,
        key=lambda row: (
            row.absolute_delta,
            row.scenario_id,
            row.weekly_wage,
        ),
    )
    maximum_emtr = max(
        emtr_rows,
        key=lambda row: (
            row.absolute_delta,
            row.scenario_id,
            row.weekly_wage,
        ),
    )
    return {
        "primary_cells": len(rows),
        "dollar_cells": len(dollar_rows),
        "dollar_cells_agree_to_cent": (
            len(dollar_rows) - len(dollar_outside_cent)
        ),
        "dollar_cells_outside_cent": len(dollar_outside_cent),
        "dollar_cells_outside_cent_by_class": {
            key: dollar_outside_cent_classes.get(key, 0)
            for key in ("match", "a", "b", "c", "d")
        },
        "exact_numeric_matches": sum(
            row.absolute_delta == 0 for row in rows
        ),
        "nonzero_deltas_within_snapshot_precision": sum(
            D0 < row.absolute_delta <= ORACLE_SIX_DECIMAL_TOLERANCE
            for row in rows
        ),
        "matches_at_six_decimal_oracle_precision": class_counts.get("match", 0),
        "differences_outside_six_decimal_envelope": (
            len(rows) - class_counts.get("match", 0)
        ),
        "classification_counts": {
            key: class_counts.get(key, 0)
            for key in ("match", "a", "b", "c", "d")
        },
        "reason_counts": dict(sorted(reason_counts.items())),
        "weekly_net_income_points_within_1_nzd": sum(
            row.absolute_delta <= D1 for row in net_income_rows
        ),
        "weekly_net_income_points": len(net_income_rows),
        "maximum_weekly_net_income_absolute_delta": maximum_net.absolute_delta,
        "maximum_weekly_net_income_delta_location": {
            "scenario_id": maximum_net.scenario_id,
            "weekly_wage": maximum_net.weekly_wage,
        },
        "maximum_emtr_absolute_delta": maximum_emtr.absolute_delta,
        "maximum_emtr_absolute_delta_percentage_points": (
            maximum_emtr.absolute_delta * Decimal(100)
        ),
        "maximum_emtr_delta_location": {
            "scenario_id": maximum_emtr.scenario_id,
            "weekly_wage": maximum_emtr.weekly_wage,
        },
        "emtr_points_within_half_percentage_point": sum(
            row.absolute_delta <= Decimal("0.005") for row in emtr_rows
        ),
        "emtr_points": len(emtr_rows),
    }


def comparison_row_json(row: ComparisonRow) -> dict[str, Any]:
    detail = CLASSIFICATION_DETAILS[row.reason_code]
    return {
        "scenario_id": row.scenario_id,
        "scenario_description": row.scenario_description,
        "weekly_wage": row.weekly_wage,
        "column": row.column,
        "unit": row.unit,
        "treasury": row.treasury,
        "rulespec": row.rulespec,
        "signed_delta_rulespec_minus_treasury": row.signed_delta,
        "absolute_delta": row.absolute_delta,
        "relative_absolute_delta": row.relative_delta,
        "classification": row.classification,
        "reason_code": row.reason_code,
        "reason_title": detail[1],
        "reason": detail[2],
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_text(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {
            str(key): json_ready(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value


def json_text(value: Any) -> str:
    return json.dumps(
        json_ready(value),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    ) + "\n"


def comparison_csv_text(rows: Sequence[ComparisonRow]) -> str:
    target = io.StringIO(newline="")
    fieldnames = (
        "scenario_id",
        "scenario_description",
        "weekly_wage",
        "column",
        "unit",
        "treasury",
        "rulespec",
        "signed_delta_rulespec_minus_treasury",
        "absolute_delta",
        "relative_absolute_delta",
        "classification",
        "reason_code",
        "reason_title",
    )
    writer = csv.DictWriter(target, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "scenario_id": row.scenario_id,
                "scenario_description": row.scenario_description,
                "weekly_wage": row.weekly_wage,
                "column": row.column,
                "unit": row.unit,
                "treasury": decimal_text(row.treasury),
                "rulespec": decimal_text(row.rulespec),
                "signed_delta_rulespec_minus_treasury": decimal_text(
                    row.signed_delta
                ),
                "absolute_delta": decimal_text(row.absolute_delta),
                "relative_absolute_delta": (
                    ""
                    if row.relative_delta is None
                    else decimal_text(row.relative_delta)
                ),
                "classification": row.classification,
                "reason_code": row.reason_code,
                "reason_title": CLASSIFICATION_DETAILS[row.reason_code][1],
            }
        )
    return target.getvalue()


def build_secondary_rate_rows(
    *,
    oracle: Mapping[str, Any],
    scenarios: Sequence[Scenario],
    sweeps: Mapping[str, Mapping[int, Mapping[str, Decimal | str | None]]],
) -> list[dict[str, Any]]:
    oracle_by_id = {str(item["id"]): item for item in oracle["scenarios"]}
    result: list[dict[str, Any]] = []
    for scenario in scenarios:
        raw = oracle_by_id[scenario.id]
        for index, wage in enumerate(scenario.sampled_wages):
            for column in ("RR", "PTR"):
                treasury_raw = raw["sampled_outputs"][index][column]
                rulespec_raw = sweeps[scenario.id][wage][column]
                treasury_value = (
                    None if treasury_raw is None else dec(treasury_raw)
                )
                if rulespec_raw is not None and not isinstance(
                    rulespec_raw, Decimal
                ):
                    raise HarnessError(
                        f"expected Decimal or null for {scenario.id} {column}"
                    )
                if treasury_value is None or rulespec_raw is None:
                    signed_delta = None
                    absolute_delta = None
                    relative_delta = None
                else:
                    signed_delta = rulespec_raw - treasury_value
                    absolute_delta = abs(signed_delta)
                    relative_delta = (
                        absolute_delta / abs(treasury_value)
                        if treasury_value != 0
                        else (D0 if absolute_delta == 0 else None)
                    )
                result.append(
                    {
                        "scenario_id": scenario.id,
                        "weekly_wage": wage,
                        "column": column,
                        "treasury": treasury_value,
                        "rulespec": rulespec_raw,
                        "signed_delta_rulespec_minus_treasury": signed_delta,
                        "absolute_delta": absolute_delta,
                        "relative_absolute_delta": relative_delta,
                    }
                )
    return result


def generic_csv_text(
    rows: Sequence[Mapping[str, Any]],
    fieldnames: Sequence[str],
) -> str:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(
        target,
        fieldnames=fieldnames,
        lineterminator="\n",
        extrasaction="ignore",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                field: (
                    ""
                    if row.get(field) is None
                    else decimal_text(row[field])
                    if isinstance(row[field], Decimal)
                    else row[field]
                )
                for field in fieldnames
            }
        )
    return target.getvalue()


def build_as_diagnostic_rows(
    *,
    oracle: Mapping[str, Any],
    scenarios: Sequence[Scenario],
    sweeps: Mapping[str, Mapping[int, Mapping[str, Decimal | str | None]]],
) -> list[dict[str, Any]]:
    oracle_by_id = {str(item["id"]): item for item in oracle["scenarios"]}
    result: list[dict[str, Any]] = []
    for scenario in scenarios:
        raw = oracle_by_id[scenario.id]
        for index, wage in enumerate(scenario.sampled_wages):
            state = sweeps[scenario.id][wage]
            before_rounding = scalar_decimal(state, "AS_Amount")
            treasury_host_aligned = scalar_decimal(
                state, "AS_Amount_treasury_host_aligned"
            )
            statutory = scalar_decimal(
                state, "AS_Amount_statutory_rounded"
            )
            treasury_value = dec(
                raw["sampled_outputs"][index]["AS_Amount"]
            )
            result.append(
                {
                    "scenario_id": scenario.id,
                    "weekly_wage": wage,
                    "treasury_raw_unrounded": treasury_value,
                    "rulespec_statutory_inputs_before_rounding": before_rounding,
                    "rulespec_treasury_host_aligned_before_rounding": (
                        treasury_host_aligned
                    ),
                    "rulespec_statutory_rounded": statutory,
                    "total_signed_delta": (
                        before_rounding - treasury_value
                    ),
                    "forecast_vintage_component_under_treasury_host_convention": (
                        treasury_host_aligned - treasury_value
                    ),
                    "statutory_host_convention_component": (
                        before_rounding - treasury_host_aligned
                    ),
                    "legal_rounding_uplift": statutory - before_rounding,
                    "rulespec_statutory_base_rate": scalar_decimal(
                        state, "AS_statutory_base_rate"
                    ),
                    "rulespec_treasury_host_base_rate": scalar_decimal(
                        state, "AS_treasury_host_base_rate"
                    ),
                    "rulespec_statutory_cutout": scalar_decimal(
                        state, "AS_statutory_cutout"
                    ),
                    "rulespec_treasury_host_cutout": scalar_decimal(
                        state, "AS_treasury_host_cutout"
                    ),
                }
            )
    return result


def build_diagnostic_rows(
    *,
    scenarios: Sequence[Scenario],
    sweeps: Mapping[str, Mapping[int, Mapping[str, Decimal | str | None]]],
) -> list[dict[str, Any]]:
    fields = (
        "AS_Amount_statutory_rounded",
        "AS_Amount_treasury_host_aligned",
        "AS_statutory_base_rate",
        "AS_treasury_host_base_rate",
        "AS_statutory_cutout",
        "AS_treasury_host_cutout",
        "gross_benefit_taxable_weekly",
        "wage2_tax",
        "wage2_ACC_levy",
        "net_wage2",
        "family_scheme_income",
        "iwtc_entitlement",
        "BestStart_Total_naive_per_child_abatement",
        "EMTR_ACC_rounding_component",
        "EMTR_WFF_complete_dollar_component",
    )
    return [
        {
            "scenario_id": scenario.id,
            "weekly_wage": wage,
            **{
                field: sweeps[scenario.id][wage][field]
                for field in fields
            },
        }
        for scenario in scenarios
        for wage in scenario.sampled_wages
    ]


def validate_emtr_residual_patterns(
    rows: Sequence[ComparisonRow],
    sweeps: Mapping[str, Mapping[int, Mapping[str, Decimal | str | None]]],
) -> list[dict[str, Any]]:
    quantum = Decimal("0.000000000001")
    diagnostics: list[dict[str, Any]] = []
    for row in rows:
        if row.column != "EMTR":
            continue
        state = sweeps[row.scenario_id][row.weekly_wage]
        acc_component = scalar_decimal(
            state, "EMTR_ACC_rounding_component"
        )
        wff_component = scalar_decimal(
            state, "EMTR_WFF_complete_dollar_component"
        )
        display_rounding_remainder = (
            row.signed_delta - acc_component - wff_component
        )
        if (
            abs(display_rounding_remainder)
            > ORACLE_SIX_DECIMAL_TOLERANCE
        ):
            raise HarnessError(
                "EMTR residual is not accounted for by ACC rounding, WFF "
                "complete-dollar arithmetic, and the six-decimal oracle "
                f"envelope at {row.scenario_id} wage {row.weekly_wage}: "
                f"{decimal_text(display_rounding_remainder)}"
            )
        diagnostics.append(
            {
                "scenario_id": row.scenario_id,
                "weekly_wage": row.weekly_wage,
                "signed_delta": row.signed_delta,
                "signed_delta_12dp": row.signed_delta.quantize(quantum),
                "acc_annual_cent_component": acc_component,
                "wff_complete_dollar_component": wff_component,
                "oracle_display_rounding_remainder": (
                    display_rounding_remainder
                ),
            }
        )
    if len(diagnostics) != 32:
        raise HarnessError(
            f"expected 32 EMTR decomposition rows, found {len(diagnostics)}"
        )

    grouped: dict[Decimal, list[dict[str, Any]]] = {}
    for item in diagnostics:
        grouped.setdefault(item["signed_delta_12dp"], []).append(item)
    patterns: list[dict[str, Any]] = []
    for signed_delta in sorted(grouped):
        members = grouped[signed_delta]
        acc_values = [
            item["acc_annual_cent_component"] for item in members
        ]
        wff_values = [
            item["wff_complete_dollar_component"] for item in members
        ]
        display_values = [
            abs(item["oracle_display_rounding_remainder"])
            for item in members
        ]
        wff_affected = sum(value != 0 for value in wff_values)
        patterns.append(
            {
                "signed_delta_12dp": signed_delta,
                "percentage_points": signed_delta * Decimal(100),
                "count": len(members),
                "acc_component_min": min(acc_values),
                "acc_component_max": max(acc_values),
                "wff_component_min": min(wff_values),
                "wff_component_max": max(wff_values),
                "maximum_absolute_oracle_display_remainder": max(
                    display_values
                ),
                "wff_affected_points": wff_affected,
                "explanation": (
                    "ACC annual-cent rounding plus MD 13 complete-dollar WFF "
                    "arithmetic and at most six-decimal oracle display rounding"
                    if wff_affected
                    else "ACC annual-cent rounding and at most six-decimal "
                    "oracle display rounding"
                ),
                "locations": [
                    {
                        "scenario_id": item["scenario_id"],
                        "weekly_wage": item["weekly_wage"],
                    }
                    for item in members
                ],
            }
        )
    return patterns


def report_number(value: Decimal, places: int = 6) -> str:
    return format(value, f".{places}f")


def report_relative(value: Decimal | None) -> str:
    if value is None:
        return "n/a"
    return f"{report_number(value * Decimal(100), 6)}%"


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def headline_text(statistics: Mapping[str, Any]) -> str:
    cent_matches = statistics["dollar_cells_agree_to_cent"]
    dollar_cells = statistics["dollar_cells"]
    outside = statistics["dollar_cells_outside_cent_by_class"]
    return (
        f"RuleSpec agrees with pinned Treasury to the cent in {cent_matches} "
        f"of {dollar_cells} dollar cells; cent-level exceptions comprise "
        f"{outside['b']} named BEFU25-versus-enacted instrument-vintage cells "
        f"and {outside['c']} documented convention cells, with "
        f"{outside['a']} remaining encoding bugs and {outside['d']} unexplained."
    )


def scenario_summary_rows(
    rows: Sequence[ComparisonRow],
    scenarios: Sequence[Scenario],
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_rows = [
            row for row in rows if row.scenario_id == scenario.id
        ]
        net_rows = [
            row for row in scenario_rows if row.column == "Net_Income"
        ]
        emtr_rows = [
            row for row in scenario_rows if row.column == "EMTR"
        ]
        classes = Counter(row.classification for row in scenario_rows)
        result.append(
            {
                "scenario_id": scenario.id,
                "points": len(net_rows),
                "net_income_within_1": sum(
                    row.absolute_delta <= D1 for row in net_rows
                ),
                "max_net_income_delta": max(
                    row.absolute_delta for row in net_rows
                ),
                "max_emtr_delta_pp": max(
                    row.absolute_delta for row in emtr_rows
                )
                * Decimal(100),
                "b_cells": classes.get("b", 0),
                "c_cells": classes.get("c", 0),
                "a_or_d_cells": (
                    classes.get("a", 0) + classes.get("d", 0)
                ),
            }
        )
    return result


def render_report(
    *,
    provenance: Provenance,
    compiled_artifact_sha256: str,
    compiled_counts: Mapping[str, int],
    engine_call_count: int,
    scenarios: Sequence[Scenario],
    rows: Sequence[ComparisonRow],
    statistics: Mapping[str, Any],
    vintage_rows: Sequence[Mapping[str, Any]],
    emtr_patterns: Sequence[Mapping[str, Any]],
    as_rows: Sequence[Mapping[str, Any]],
) -> str:
    headline = headline_text(statistics)
    emtr_wff_points = sum(
        int(item["wff_affected_points"]) for item in emtr_patterns
    )
    emtr_acc_only_points = 32 - emtr_wff_points
    maximum_emtr_display_remainder = max(
        item["maximum_absolute_oracle_display_remainder"]
        for item in emtr_patterns
    )
    material_as_rows = [
        item
        for item in as_rows
        if abs(item["total_signed_delta"])
        > ORACLE_SIX_DECIMAL_TOLERANCE
    ]
    material_as_count = len(material_as_rows)
    lines: list[str] = [
        "# Treasury IncomeExplorer EMTR reproduction audit",
        "",
        "## Headline",
        "",
        f"> {headline}",
        "",
        "This is a comparison against the pinned output of Treasury's raw "
        "`R/emtr.R#emtr` function, not against the IncomeExplorer UI wrapper. "
        "The final matrix has 640 primary cells: 4 scenarios × 8 wage points × "
        "19 dollar/control columns plus EMTR.",
        "",
        "## What we can honestly say",
        "",
        "> We cannot claim an end-to-end reproduction of IncomeExplorer; this "
        "audit provides a reproducible, pointwise comparison of RuleSpec's "
        "enacted 2026/27 amount rules against a pinned TY27 BEFU25 output of "
        "Treasury's raw `emtr()` function for four stylised families, "
        "conditional on explicit host-side eligibility assumptions.",
        "",
        f"The numerical result is: {headline}",
        "",
        "## Result summary",
        "",
        "| Measure | Result |",
        "|---|---:|",
        (
            "| Exact numeric matches | "
            f"{statistics['exact_numeric_matches']} / "
            f"{statistics['primary_cells']} |"
        ),
        (
            "| Additional matches inside six-decimal snapshot envelope | "
            f"{statistics['nonzero_deltas_within_snapshot_precision']} |"
        ),
        (
            "| Differences outside six-decimal snapshot envelope | "
            f"{statistics['differences_outside_six_decimal_envelope']} / "
            f"{statistics['primary_cells']} |"
        ),
        (
            "| Weekly Net Income within $1 | "
            f"{statistics['weekly_net_income_points_within_1_nzd']} / 32 |"
        ),
        (
            "| Maximum weekly Net Income absolute delta | "
            f"${report_number(statistics['maximum_weekly_net_income_absolute_delta'], 6)} "
            f"at `{statistics['maximum_weekly_net_income_delta_location']['scenario_id']}`, "
            f"wage ${statistics['maximum_weekly_net_income_delta_location']['weekly_wage']} |"
        ),
        (
            "| EMTR within 0.5 percentage point | "
            f"{statistics['emtr_points_within_half_percentage_point']} / 32 |"
        ),
        (
            "| Maximum EMTR absolute delta | "
            f"{report_number(statistics['maximum_emtr_absolute_delta_percentage_points'], 6)} "
            "percentage points |"
        ),
        (
            "| Remaining class-(a) encoding bugs | "
            f"{statistics['classification_counts']['a']} |"
        ),
        (
            "| Genuinely unexplained class-(d) cells | "
            f"{statistics['classification_counts']['d']} |"
        ),
        "",
        "Scenario-level summary:",
        "",
        "| Scenario | NI within $1 | Max weekly NI |Δ| | Max EMTR |Δ| (pp) | "
        "(b) cells | (c) cells | (a)+(d) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in scenario_summary_rows(rows, scenarios):
        lines.append(
            f"| `{item['scenario_id']}` | {item['net_income_within_1']} / 8 | "
            f"${report_number(item['max_net_income_delta'], 6)} | "
            f"{report_number(item['max_emtr_delta_pp'], 6)} | "
            f"{item['b_cells']} | {item['c_cells']} | "
            f"{item['a_or_d_cells']} |"
        )

    lines.extend(
        [
            "",
            "The comparison treats an absolute delta of at most "
            "`0.0000005` as a match because the pinned JSON generator rounded "
            "every numeric output to six decimals. Raw deltas are retained in "
            "[comparison.csv](comparison.csv) and "
            "[comparison.json](comparison.json); they are not zeroed.",
            "",
            "## Discrepancy classification",
            "",
            "| Class | Cells | Conclusion |",
            "|---|---:|---|",
            (
                f"| match | {statistics['classification_counts']['match']} | "
                "Exact or within the oracle's six-decimal rounding envelope. |"
            ),
            (
                f"| (a) our encoding bug | "
                f"{statistics['classification_counts']['a']} | "
                + (
                    "No class-(a) residual remains in the final matrix. |"
                    if statistics["classification_counts"]["a"] == 0
                    else "See the classified matrix rows below. |"
                )
            ),
            (
                f"| (b) BEFU25 vs enacted law | "
                f"{statistics['classification_counts']['b']} | "
                "Prescribed benefit/credit levels or their downstream effects. |"
            ),
            (
                f"| (c) unit/period convention | "
                f"{statistics['classification_counts']['c']} | "
                "Annual-cent or complete-dollar statutory arithmetic viewed "
                "through a weekly $1 interval. |"
            ),
            (
                f"| (d) unexplained | "
                f"{statistics['classification_counts']['d']} | "
                + (
                    "No difference outside the snapshot envelope is assigned "
                    "class (d) under the documented classification. |"
                    if statistics["classification_counts"]["d"] == 0
                    else "See the unexplained matrix rows below. |"
                )
            ),
            "",
            "Two genuine class-(a) defects were found during the audit and "
            "corrected before this final run. First, the lone-parent "
            "Accommodation Supplement cutout initially used the staged "
            "SPS/JSS-with-children test; Treasury's source-defined branch "
            "combines the lone-parent JSS base with the flat JSS scale. That "
            "correction follows Social Security Act 2018 Schedule 2 Income "
            "Tests 1 and 3 and is checkpointed in local audit commit `3364877`. "
            "Second, the initial AS primary retained Treasury's host conventions "
            "for delegated inputs. The final statutory primary instead follows "
            "Social Security Regulations 2018 reg 17 (annual eldest FTC divided "
            "by 52) and reg 18 (the exact income that extinguishes JSS). "
            "Treasury's `365/7` divisor and annual-dollar ceiling are now a "
            "labeled diagnostic only. The final sweep's class-(a) count is "
            f"{statistics['classification_counts']['a']}.",
            "",
            "Observed reason codes:",
            "",
            "| Code | Class | Cells | Evidence |",
            "|---|:---:|---:|---|",
        ]
    )
    observed_reasons = Counter(row.reason_code for row in rows)
    for reason_code in sorted(observed_reasons):
        category, title, explanation = CLASSIFICATION_DETAILS[reason_code]
        lines.append(
            f"| `{reason_code}` | {category} | "
            f"{observed_reasons[reason_code]} | "
            f"{markdown_cell(title)} — {markdown_cell(explanation)} |"
        )

    lines.extend(
        [
            "",
            "### Class (b): pinned forecast vintage versus enacted 2026/27 law",
            "",
            "Treasury commit `741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b` "
            "(12 August 2025) pins `TY27_BEFU25.yaml`. RuleSpec selects law "
            "effective 1 April 2026. These are different vintages, not errors "
            "on either side.",
            "",
            "| Parameter | Treasury BEFU25 | RuleSpec enacted | Signed delta | "
            "Unit | Statutory source |",
            "|---|---:|---:|---:|---|---|",
        ]
    )
    for item in vintage_rows:
        lines.append(
            f"| {markdown_cell(item['label'])} | "
            f"{report_number(item['treasury_befu25'], 2)} | "
            f"{report_number(item['rulespec_enacted'], 2)} | "
            f"{report_number(item['signed_delta'], 2)} | "
            f"{item['unit']} | {markdown_cell(item['statute'])}; "
            f"`{item['corpus_citation_path']}` |"
        )
    lines.extend(
        [
            "",
            "The benefit evidence is Social Security Act 2018 Schedule 4 "
            "Parts 1–2, as amended by the Social Security (Rates of Benefits "
            "and Allowances) Order 2026 clause 5. The WFF evidence is Income "
            "Tax Act 2007 ss MD 3, MD 10, ME 1, and MG 2. The "
            "[Income Tax (Tax Credit) Order 2025]"
            "(https://www.legislation.govt.nz/secondary-legislation/"
            "pco-drafted/2025/260/en/latest/) cls 4–6 establishes the "
            "post-snapshot 2026/27 FTC, MFTC, and Best Start amounts. The "
            "2026/27 IWTC $7,670 base is enacted by the Taxation (Annual Rates "
            "for 2025-26, "
            "Compliance Simplification, and Remedial Measures) Act 2026 "
            "ss 2 and 105. Local evidence bundles are:",
            "",
            "- `data/corpus/provisions/nz/statute/"
            "2026-06-17-social-security-main-benefit-rates.jsonl`",
            "- `data/corpus/provisions/nz/statute/"
            "2026-06-17-wff-tax-credits.jsonl`",
            "",
            "Accommodation Supplement maxima themselves do not explain the "
            f"{material_as_count} AS differences outside the envelope. Each AS "
            "row is decomposed into (1) the BEFU25-versus-enacted difference "
            "under Treasury's own host conventions and (2) the additional "
            "statutory host-convention difference: reg 17 divides annual eldest "
            "FTC by 52, while raw Treasury divides by `365/7`; reg 18 uses the "
            "exact JSS vanishing point, while raw Treasury applies an annual-"
            "dollar ceiling. A row is class (b) only when its Treasury-host-"
            "aligned diagnostic independently has a vintage difference; the "
            "smaller class-(c) component is disclosed rather than folded into "
            "the vintage claim. The primary matrix uses RuleSpec's statutory "
            "inputs before reg 19 whole-dollar rounding. All components and the "
            "legally rounded payment are preserved in "
            "[as_rounding_diagnostic.csv](as_rounding_diagnostic.csv).",
            "",
            "### Class (c): period and rounding convention",
            "",
            "The engine performs no automatic period conversion. The harness "
            "uses these explicit alignments:",
            "",
            "| Component | RuleSpec source period | Treasury comparison |",
            "|---|---|---|",
            "| Main benefits | Weekly amount (despite a legacy `period: Year` "
            "label) | No conversion |",
            "| Income tax, ACC, FTC, Best Start, IETC | Annual | Divide by "
            "`365/7` |",
            "| IWTC base and MFTC | Annual rules expressed over weekly periods "
            "| Divide by `52` |",
            "| IWTC abatement | Annual | Divide by `365/7`, then subtract from "
            "the `/52` base |",
            "| WFF total | Mixed | Add converted FTC and IWTC components; do "
            "not divide the aggregate once |",
            "| Winter Energy Payment | Per-winter total | Divide by `365/7` to "
            "match Treasury's annual-average snapshot convention |",
            "| Accommodation Supplement | Weekly; reg 17 annual FTC input is "
            "divided by 52 | No output conversion; compare the statutory-input "
            "pre-round amount and emit a Treasury-host-aligned diagnostic |",
            "",
            "Treasury applies ACC as an unrounded weekly 1.75%. RuleSpec applies "
            "the annual including-GST PAYE levy and whole-cent rounding before "
            "weekly conversion. The RuleSpec source is Accident Compensation "
            "(Earners' Levy) Regulations 2025 regs 4, 5, and 8 plus Inland "
            "Revenue's 1.75% PAYE-facing rate; local evidence is "
            "`data/corpus/provisions/nz/regulation/"
            "2026-06-17-acc-earners-levy-2025-formulas.jsonl` and "
            "`data/corpus/provisions/nz/agency/"
            "2026-06-17-ird-acc-levy-rates.jsonl`.",
            "",
            f"All 32 EMTR residuals fall into {len(emtr_patterns)} "
            "source-consistent numerical patterns. For each interval the "
            "harness calculates the RuleSpec annual-cent ACC component and "
            "MD 13 complete-dollar WFF component; any remainder must fit inside "
            "the oracle's six-decimal envelope before this report is written:",
            "",
            "| RuleSpec − Treasury EMTR | Percentage points | Points | "
            "WFF-affected | Max display remainder | Decomposition |",
            "|---:|---:|---:|---:|---:|---|",
        ]
    )
    for item in emtr_patterns:
        lines.append(
            f"| {report_number(item['signed_delta_12dp'], 12)} | "
            f"{report_number(item['percentage_points'], 9)} | "
            f"{item['count']} | {item['wff_affected_points']} | "
            f"{report_number(item['maximum_absolute_oracle_display_remainder'], 12)} | "
            f"{item['explanation']} |"
        )
    lines.extend(
        [
            "",
            f"The {emtr_wff_points} WFF-affected intervals are consistent with "
            "the "
            "interaction between "
            "Income Tax Act 2007 s MD 13's complete-dollar abatement base and a "
            f"$1 weekly step (`365/7` annual dollars). The other "
            f"{emtr_acc_only_points} intervals have no computed WFF component. "
            "The maximum remainder after ACC and WFF decomposition is "
            f"`{decimal_text(maximum_emtr_display_remainder)}`, within the "
            "six-decimal JSON envelope. This calculation supports class (c) "
            "for the EMTR rows; any interval outside that envelope would be "
            "classified (d).",
            "",
            "## Method",
            "",
            "1. Verify the pinned oracle commit, parameter-file hash, RuleSpec "
            "SHA, engine SHA, composition hash, and clean tracked RuleSpec and "
            "engine source trees.",
            "2. Compile the ten-module composition from scratch in a temporary "
            "directory and execute every query in engine `explain` mode.",
            "3. Map each stylised profile to explicit person, child, and family "
            "inputs. The compiled program has no relations, so aggregation is "
            "performed transparently in the host harness.",
            "   Treasury's raw branch threshold "
            "`1226.7 / 52.2 = $23.50/week` is retained host-side: when the "
            "pinned model enables IWTC and disallows IWTC to beneficiaries, "
            "that branch zeroes benefit amounts. This is a disclosed raw-source "
            "flow convention, not a RuleSpec policy parameter.",
            "   Wage tax is calculated as tax on grossed taxable benefit plus "
            "wages minus tax on grossed taxable benefit, matching raw "
            "`emtr()` rather than taxing wages in isolation.",
            "4. Evaluate the eight displayed weekly wages plus each hidden "
            "`w+1` endpoint and `$1,499`.",
            "5. Calculate `EMTR = 1 - (NetIncome(w+1) - NetIncome(w))`. At the "
            "$1,500 display point, carry the `$1,499 → $1,500` interval, exactly "
            "matching Treasury's `zoo::na.locf` endpoint convention.",
            "6. Compare RuleSpec against Treasury without replacing or tuning "
            "any RuleSpec parameter. Signed deltas are always RuleSpec minus "
            "Treasury; the report matrix shows absolute and relative deltas.",
            "",
            "Treasury's app does something different: its server calls "
            "`calculate_income()`, whose `WFF_or_Benefit: Max` wrapper may "
            "select between transfers. The pinned snapshot explicitly calls "
            "raw `emtr()` and bypasses that wrapper, so this audit does too.",
            "",
            "## Coverage gaps",
            "",
            "This is a conditional amount comparison, not a legal entitlement "
            "determination. The snapshot supplies only partnered status, an "
            "hourly wage, child ages, partner wage/hours, housing costs/type, "
            "and AS area. It does not supply all facts required by the statutes.",
            "",
            "- Main-benefit residence, immigration, work availability, medical, "
            "student, strike, concurrent-benefit, and other entitlement facts "
            "are not established. Adult age 25 and other profile facts are host "
            "assumptions. The amount schedules are evaluated conditionally.",
            "- FTC and Best Start use full-year entitlement days and full care "
            "for the listed children. Full principal-caregiver, residence, "
            "shared-care, date-of-birth/due-date, and parental-leave conditions "
            "are not established.",
            "- IWTC's statutory eligibility closure is populated with explicit "
            "stylised assumptions because the snapshot omits those facts. MFTC "
            "full-time/no-benefit eligibility is inferred from the raw model's "
            "profile convention.",
            "- IETC residence and disqualifying-support conditions are assumed, "
            "not evidenced by the snapshot.",
            "- Winter Energy Payment uses the RuleSpec per-winter rate, host-"
            "gated only when the RuleSpec-side reconstruction has positive net "
            "benefit (mirroring Treasury's raw gate), and annual-averaged. Full "
            "legal entitlement, election, absence, and care-facility rules "
            "under Social Security Act 2018 ss 71–75 and 220 are not evaluated.",
            "- Accommodation Supplement compares the amount formula before "
            "legal rounding and assumes eligibility/takeup. Assets, social "
            "housing, student allowance, residential/disability care, duplicate "
            "partner claims, and other ss 65–69 exclusions are not evaluated.",
            "- The lone-parent profile in this grid has children aged 0, 1, and "
            "10. The harness does not generalise Treasury's separate lone-parent "
            "JSS branch for a youngest child aged 14 or over.",
            "- The only profile with two Best Start-aged children remains below "
            "the $79,000 abatement threshold throughout the requested grid. "
            "This audit therefore does not test Treasury's aggregate-child "
            "abatement against RuleSpec's per-child composition above that "
            "threshold.",
            "- RR and PTR are computed and emitted in "
            "[secondary_rates.csv](secondary_rates.csv), but are outside the "
            "requested dollar-plus-EMTR validation matrix.",
            "- Person/child/family aggregation is host-side because the compiled "
            "composition has no relations.",
            "",
            "Treasury itself describes the UI profiles as theoretical, assumes "
            "full AS take-up, omits the AS asset test, and excludes NZ Super, "
            "FamilyBoost, Supported Living Payment, youth payments, IRRS/TAS, "
            "KiwiSaver, student loans/allowances, paid parental leave, and child "
            "support pass-on. Those programs are not silently filled in here.",
            "",
            "## Provenance and reproducibility",
            "",
            "| Item | Verified value |",
            "|---|---|",
            f"| Oracle snapshot SHA-256 | `{provenance.oracle_sha256}` |",
            f"| Treasury commit | `{EXPECTED_ORACLE_COMMIT}` |",
            f"| Treasury parameter SHA-256 | `{EXPECTED_PARAMETER_SHA256}` |",
            f"| RuleSpec commit | `{provenance.rulespec_sha}` |",
            f"| Engine source checkout commit | `{provenance.engine_sha}` |",
            f"| Executed engine binary SHA-256 | "
            f"`{provenance.engine_binary_sha256}` |",
            f"| Composition SHA-256 | `{provenance.composition_sha256}` |",
            f"| Compiled artifact SHA-256 | `{compiled_artifact_sha256}` |",
            f"| Compiled derived outputs | "
            f"{compiled_counts['derived_outputs']} total (174 imported + 2 "
            "bridge rules) |",
            f"| Compiled parameters | {compiled_counts['parameters']} |",
            f"| Compiled input slots | {compiled_counts['input_slots']} |",
            f"| Engine evaluations in one fresh pass | {engine_call_count} |",
            "| Tax-year interval | `2026-04-01` to `2027-03-31` |",
            "",
            "Run from the Foundation workspace:",
            "",
            "```sh",
            "python3 ops/nz-lane/emtr_reproduction/run.py",
            "```",
            "",
            "The command performs two independent fresh compilations and "
            "evaluations in temporary directories, compares every generated "
            "artifact byte-for-byte, and only then writes the output files. "
            "`SHA256SUMS` covers every report/data artifact. No network access "
            "or manual intermediate file is required.",
            "",
            "This should not yet graduate into `rulespec-nz` as a claim of "
            "Treasury reproduction. After the entitlement closures and the "
            "forecast-vintage/enacted-law baseline are made explicit product "
            "choices, the pinned matrix would be valuable as a dual-vintage "
            "regression test.",
            "",
            "## Full comparison matrix",
            "",
            "Values are weekly unless the unit says annual. `|Δ|` is the "
            "absolute delta; relative delta is `|RuleSpec − Treasury| / "
            "|Treasury|`. An exact zero-over-zero match is shown as `0%`; "
            "otherwise a zero Treasury denominator is `n/a`. The exact "
            "signed deltas and unrounded engine decimals are in "
            "[comparison.csv](comparison.csv).",
            "",
        ]
    )

    rows_by_scenario: dict[str, list[ComparisonRow]] = {
        scenario.id: [] for scenario in scenarios
    }
    for row in rows:
        rows_by_scenario[row.scenario_id].append(row)
    for scenario in scenarios:
        lines.extend(
            [
                f"### `{scenario.id}`",
                "",
                scenario.description,
                "",
                "| Wage | Metric | Unit | Treasury | RuleSpec | Abs delta | "
                "Relative | Class |",
                "|---:|---|---|---:|---:|---:|---:|---|",
            ]
        )
        for row in rows_by_scenario[scenario.id]:
            class_label = (
                "match"
                if row.classification == "match"
                else f"({row.classification}) `{row.reason_code}`"
            )
            lines.append(
                f"| {row.weekly_wage} | `{row.column}` | {row.unit} | "
                f"{report_number(row.treasury, 6)} | "
                f"{report_number(row.rulespec, 6)} | "
                f"{report_number(row.absolute_delta, 9)} | "
                f"{report_relative(row.relative_delta)} | {class_label} |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_audit_artifacts(
    *,
    rulespec_root: Path,
    engine_root: Path,
    engine_binary: Path,
    treasury_root: Path,
    composition_path: Path,
    oracle_generator: Path,
    rscript: Path,
) -> tuple[dict[str, str], dict[str, Any]]:
    regenerated = regenerate_treasury_oracles(
        rulespec_root=rulespec_root,
        treasury_root=treasury_root,
        oracle_generator=oracle_generator,
        rscript=rscript,
    )
    oracle, provenance = verify_inputs(
        regenerated=regenerated,
        rulespec_root=rulespec_root,
        engine_root=engine_root,
        engine_binary=engine_binary,
        treasury_root=treasury_root,
        composition_path=composition_path,
        oracle_generator=oracle_generator,
        rscript=rscript,
    )
    with tempfile.TemporaryDirectory(prefix="axiom-emtr-fresh-") as raw_temp:
        temp_root = Path(raw_temp)
        compiled_path = temp_root / "composition.json"
        engine, compiled, _compile_stdout = Engine.compile(
            binary=provenance.engine_binary,
            composition=provenance.composition_path,
            rulespec_root=provenance.rulespec_root,
            artifact=compiled_path,
        )
        compiled_artifact_sha256 = sha256_file(compiled_path)
        compiled_counts = {
            "derived_outputs": len(compiled["program"]["derived"]),
            "parameters": len(compiled["program"]["parameters"]),
            "input_slots": len(
                compiled["metadata"]["input_catalog"]
            ),
            "relations": len(compiled["program"]["relations"]),
        }
        if compiled_counts != {
            "derived_outputs": 176,
            "parameters": 129,
            "input_slots": 328,
            "relations": 0,
        }:
            raise HarnessError(
                f"unexpected composition shape: {compiled_counts!r}"
            )

        scenarios = [
            Scenario.from_oracle(
                raw,
                oracle["scenario_provenance"][str(raw["id"])],
            )
            for raw in oracle["scenarios"]
        ]
        evaluator = ModelEvaluator(engine, compiled)
        sweeps = {
            scenario.id: sweep_scenario(evaluator, scenario)
            for scenario in scenarios
        }
        comparison_rows = build_comparison_rows(
            oracle=oracle,
            scenarios=scenarios,
            sweeps=sweeps,
        )
        statistics = summary_statistics(comparison_rows)
        vintage_rows = build_vintage_parameter_rows(compiled, provenance)
        emtr_patterns = validate_emtr_residual_patterns(
            comparison_rows, sweeps
        )
        secondary_rows = build_secondary_rate_rows(
            oracle=oracle,
            scenarios=scenarios,
            sweeps=sweeps,
        )
        as_rows = build_as_diagnostic_rows(
            oracle=oracle,
            scenarios=scenarios,
            sweeps=sweeps,
        )
        diagnostic_rows = build_diagnostic_rows(
            scenarios=scenarios,
            sweeps=sweeps,
        )

        scenario_json = [
            {
                "id": scenario.id,
                "description": scenario.description,
                "inputs": {
                    "partnered": scenario.partnered,
                    "wage1_hourly": scenario.wage1_hourly,
                    "children_ages": scenario.children,
                    "gross_wage2": scenario.gross_wage2,
                    "hours2": scenario.hours2,
                    "accommodation_costs": scenario.accommodation_costs,
                    "accommodation_rent": scenario.accommodation_rent,
                    "accommodation_area": scenario.accommodation_area,
                    "accommodation_boarder": scenario.accommodation_boarder,
                    "weekly_board_and_lodgings_paid": (
                        scenario.weekly_board_and_lodgings_paid
                    ),
                },
                "sampled_weekly_wages": scenario.sampled_wages,
                "provenance": oracle["scenario_provenance"][scenario.id],
            }
            for scenario in scenarios
        ]
        machine_payload = {
            "schema_version": 1,
            "headline": headline_text(statistics),
            "scope": {
                "comparison_target": (
                    "pinned Treasury raw R/emtr.R#emtr snapshot"
                ),
                "not_compared": (
                    "IncomeExplorer calculate_income UI wrapper and "
                    "WFF_or_Benefit: Max"
                ),
                "tax_year": {
                    "start": EXPECTED_PERIOD_START,
                    "end": EXPECTED_PERIOD_END,
                },
                "displayed_weekly_wages": EXPECTED_SAMPLE_WAGES,
                "sampled_weekly_wages_by_scenario": {
                    scenario.id: scenario.sampled_wages
                    for scenario in scenarios
                },
                "primary_columns": COMPARISON_COLUMNS,
                "oracle_match_tolerance": ORACLE_SIX_DECIMAL_TOLERANCE,
            },
            "provenance": provenance.as_json(),
            "compiled_program": {
                **compiled_counts,
                "artifact_sha256": compiled_artifact_sha256,
                "engine_evaluations": engine.call_count,
            },
            "methodology": {
                "emtr": (
                    "weekly $1 forward difference; the displayed $1,500 "
                    "value carries the $1,499 to $1,500 interval"
                ),
                "delta_sign": "rulespec minus treasury",
                "period_conversions": {
                    "tax_acc_ftc_best_start_ietc": "divide annual by 365/7",
                    "benefits": "already weekly; no conversion",
                    "iwtc_base_mftc": "divide annual by 52",
                    "iwtc_abatement": "divide annual by 365/7",
                    "winter_energy": (
                        "divide per-winter amount by 365/7 for snapshot "
                        "annual-average convention"
                    ),
                    "accommodation_supplement": (
                        "weekly statutory primary: reg 17 FTC /52, exact reg "
                        "18 JSS cutout, before reg 19 rounding; Treasury-host-"
                        "aligned inputs emitted only as diagnostics"
                    ),
                },
                "determinism": (
                    "CLI performs two independent fresh compile/evaluate "
                    "passes and requires byte-identical artifacts"
                ),
                "parameter_policy": (
                    "no Treasury amount is injected as a RuleSpec parameter; "
                    "the disclosed raw-flow IWTC branch threshold is retained "
                    "host-side"
                ),
            },
            "statistics": statistics,
            "classification_definitions": {
                code: {
                    "classification": detail[0],
                    "title": detail[1],
                    "explanation": detail[2],
                }
                for code, detail in sorted(
                    CLASSIFICATION_DETAILS.items()
                )
            },
            "vintage_parameter_evidence": vintage_rows,
            "emtr_residual_patterns": emtr_patterns,
            "scenarios": scenario_json,
            "comparisons": [
                comparison_row_json(row)
                for row in comparison_rows
            ],
            "secondary_rates": secondary_rows,
            "accommodation_supplement_rounding_diagnostics": as_rows,
            "engine_state_diagnostics": diagnostic_rows,
            "coverage_statement": (
                "Conditional stylised-family amount comparison; not full "
                "statutory entitlement evaluation or UI reproduction."
            ),
        }

        report = render_report(
            provenance=provenance,
            compiled_artifact_sha256=compiled_artifact_sha256,
            compiled_counts=compiled_counts,
            engine_call_count=engine.call_count,
            scenarios=scenarios,
            rows=comparison_rows,
            statistics=statistics,
            vintage_rows=vintage_rows,
            emtr_patterns=emtr_patterns,
            as_rows=as_rows,
        )
        artifacts: dict[str, str] = {
            "REPORT.md": report,
            EXPANDED_ORACLE_NAME: regenerated.expanded_text,
            "comparison.csv": comparison_csv_text(comparison_rows),
            "comparison.json": json_text(machine_payload),
            "secondary_rates.csv": generic_csv_text(
                secondary_rows,
                (
                    "scenario_id",
                    "weekly_wage",
                    "column",
                    "treasury",
                    "rulespec",
                    "signed_delta_rulespec_minus_treasury",
                    "absolute_delta",
                    "relative_absolute_delta",
                ),
            ),
            "as_rounding_diagnostic.csv": generic_csv_text(
                as_rows,
                (
                    "scenario_id",
                    "weekly_wage",
                    "treasury_raw_unrounded",
                    "rulespec_statutory_inputs_before_rounding",
                    "rulespec_treasury_host_aligned_before_rounding",
                    "rulespec_statutory_rounded",
                    "total_signed_delta",
                    "forecast_vintage_component_under_treasury_host_convention",
                    "statutory_host_convention_component",
                    "legal_rounding_uplift",
                    "rulespec_statutory_base_rate",
                    "rulespec_treasury_host_base_rate",
                    "rulespec_statutory_cutout",
                    "rulespec_treasury_host_cutout",
                ),
            ),
        }
        artifacts["SHA256SUMS"] = "".join(
            f"{hashlib.sha256(content.encode('utf-8')).hexdigest()}  {name}\n"
            for name, content in sorted(artifacts.items())
        )
        run_summary = {
            "headline": machine_payload["headline"],
            "statistics": statistics,
            "compiled_artifact_sha256": compiled_artifact_sha256,
            "engine_evaluations": engine.call_count,
            "artifact_names": tuple(sorted(artifacts)),
        }
        return artifacts, run_summary


def compare_fresh_artifacts(
    first: Mapping[str, str],
    second: Mapping[str, str],
) -> None:
    if set(first) != set(second):
        raise HarnessError(
            "fresh runs generated different artifact names: "
            f"{sorted(first)} != {sorted(second)}"
        )
    mismatches = [
        name
        for name in sorted(first)
        if first[name].encode("utf-8") != second[name].encode("utf-8")
    ]
    if mismatches:
        details = {
            name: (
                hashlib.sha256(first[name].encode("utf-8")).hexdigest(),
                hashlib.sha256(second[name].encode("utf-8")).hexdigest(),
            )
            for name in mismatches
        }
        raise HarnessError(
            f"fresh-run artifacts are not deterministic: {details!r}"
        )


def write_artifacts(output_dir: Path, artifacts: Mapping[str, str]) -> None:
    destination = output_dir.expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(artifacts.items()):
        (destination / name).write_text(content, encoding="utf-8")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce the pinned Treasury EMTR comparison with RuleSpec NZ"
        )
    )
    parser.add_argument(
        "--rulespec-root",
        type=Path,
        default=DEFAULT_RULESPEC_ROOT,
    )
    parser.add_argument(
        "--engine-root",
        type=Path,
        default=DEFAULT_ENGINE_ROOT,
    )
    parser.add_argument(
        "--engine-binary",
        type=Path,
        default=None,
        help=(
            "Defaults to <engine-root>/target/release/"
            "axiom-rules-engine"
        ),
    )
    parser.add_argument(
        "--treasury-root",
        type=Path,
        default=DEFAULT_TREASURY_ROOT,
    )
    parser.add_argument(
        "--composition",
        type=Path,
        default=DEFAULT_COMPOSITION,
    )
    parser.add_argument(
        "--oracle-generator",
        type=Path,
        default=DEFAULT_ORACLE_GENERATOR,
    )
    parser.add_argument(
        "--rscript",
        type=Path,
        default=DEFAULT_RSCRIPT,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=HERE,
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    engine_binary = (
        args.engine_binary
        if args.engine_binary is not None
        else args.engine_root / "target" / "release" / "axiom-rules-engine"
    )
    try:
        first, summary = build_audit_artifacts(
            rulespec_root=args.rulespec_root,
            engine_root=args.engine_root,
            engine_binary=engine_binary,
            treasury_root=args.treasury_root,
            composition_path=args.composition,
            oracle_generator=args.oracle_generator,
            rscript=args.rscript,
        )
        second, second_summary = build_audit_artifacts(
            rulespec_root=args.rulespec_root,
            engine_root=args.engine_root,
            engine_binary=engine_binary,
            treasury_root=args.treasury_root,
            composition_path=args.composition,
            oracle_generator=args.oracle_generator,
            rscript=args.rscript,
        )
        compare_fresh_artifacts(first, second)
        if json_text(summary) != json_text(second_summary):
            raise HarnessError(
                "fresh-run summaries are not deterministic"
            )
        write_artifacts(args.output_dir, first)
    except HarnessError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            json_ready(
                {
                    **summary,
                    "deterministic_fresh_runs": 2,
                    "output_dir": str(
                        args.output_dir.expanduser().resolve()
                    ),
                }
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
