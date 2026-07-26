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
import json
import subprocess
import sys
import tempfile
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
EXPECTED_SAMPLE_WAGES = (0, 160, 250, 370, 555, 740, 1000, 1500)
EXPECTED_SCENARIOS = (
    "single_parent_three_children_area1_rent",
    "couple_two_children_area2_mortgage",
    "couple_one_child_partner_10h_area3_rent",
    "single_no_children_area2_no_housing_costs",
)
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

D0 = Decimal(0)
D1 = Decimal(1)
D7 = Decimal(7)
D52 = Decimal(52)
D365 = Decimal(365)
WEEKS_IN_MODEL_YEAR = D365 / D7
ENGINE_DECIMAL_TOLERANCE = Decimal("0.000000000000000001")

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


def verify_inputs(
    *,
    rulespec_root: Path,
    engine_root: Path,
    engine_binary: Path,
    treasury_root: Path,
    composition_path: Path,
) -> tuple[dict[str, Any], Provenance]:
    rulespec_root = require_directory(rulespec_root, "RuleSpec root")
    engine_root = require_directory(engine_root, "engine root")
    engine_binary = require_file(engine_binary, "engine binary")
    composition_path = require_file(composition_path, "composition")

    if rulespec_root.name != "rulespec-nz":
        raise HarnessError(
            f"RuleSpec root basename must be rulespec-nz, got {rulespec_root.name!r}"
        )

    oracle_path = require_file(
        rulespec_root / "data" / "oracles" / "treasury-emtr-snapshot.json",
        "Treasury oracle snapshot",
    )
    with oracle_path.open(encoding="utf-8") as source:
        oracle = json.load(source)

    pinned = oracle.get("oracle", {})
    checks: tuple[tuple[str, Any, Any], ...] = (
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

    treasury_root = treasury_root.expanduser().resolve()
    treasury_present = treasury_root.is_dir()
    treasury_sha: str | None = None
    parameter_sha: str | None = None
    if treasury_present:
        treasury_sha = git_sha(treasury_root)
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
        oracle_sha256=sha256_file(oracle_path),
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

    @classmethod
    def from_oracle(cls, raw: Mapping[str, Any]) -> "Scenario":
        inputs = raw["inputs"]
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
        self._as_cutout_cache: dict[tuple[bool, int], Decimal] = {}
        self.tax_rates = selected_parameter_values(
            compiled, "individual_income_tax_bracket_rates"
        )
        self.tax_thresholds = selected_parameter_values(
            compiled, "individual_income_tax_bracket_thresholds"
        )
        self.ftc_eldest_annual = selected_parameter_values(
            compiled, "family_tax_credit_eldest_child_annual_amount"
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
    ) -> Decimal:
        eligible_children = [
            index for index, age in enumerate(scenario.children) if age in (0, 1, 2)
        ]
        total = D0
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
                outputs=[BEST_START_OUTPUT],
            )
            total += scalar_decimal(values, BEST_START_OUTPUT)
        return total / WEEKS_IN_MODEL_YEAR

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

    def accommodation_cutout(self, scenario: Scenario) -> Decimal:
        key = (scenario.partnered, len(scenario.children))
        if key in self._as_cutout_cache:
            return self._as_cutout_cache[key]
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
        annual_ceiling = (
            raw_cutout * WEEKS_IN_MODEL_YEAR
        ).to_integral_value(rounding=ROUND_CEILING)
        cutout = annual_ceiling / WEEKS_IN_MODEL_YEAR
        self._as_cutout_cache[key] = cutout
        return cutout

    def accommodation_values(
        self,
        *,
        scenario: Scenario,
        weekly_wages: Decimal,
        net_benefit: Decimal,
        eldest_ftc_annual: Decimal,
    ) -> tuple[Decimal, Decimal]:
        zero_income_benefit = sum(
            self.zero_income_jobseeker_components(scenario), D0
        )
        base_rate = zero_income_benefit
        if scenario.children:
            base_rate += eldest_ftc_annual / WEEKS_IN_MODEL_YEAR
        rent = scenario.accommodation_rent
        area = scenario.accommodation_area
        inputs: dict[str, bool | int | Decimal] = {
            "accommodation_supplement_additional_resident_in_social_housing": False,
            "accommodation_supplement_area_let_to_nonresidents": D0,
            "accommodation_supplement_base_rate_weekly_amount": base_rate,
            "accommodation_supplement_boarder": False,
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
                self.accommodation_cutout(scenario)
            ),
            "accommodation_supplement_owner_weekly_payment_share": D0,
            "accommodation_supplement_owner_weekly_required_payments": (
                scenario.accommodation_costs if not rent else D0
            ),
            "accommodation_supplement_owns_premises_and_not_joint_owner_with_resident": (
                not rent
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
            "accommodation_supplement_weekly_board_and_lodgings_paid": D0,
            "accommodation_supplement_weekly_boarder_payments_received": D0,
            "accommodation_supplement_weekly_contributions_received_from_additional_residents": D0,
            "accommodation_supplement_weekly_rent_paid": (
                scenario.accommodation_costs if rent else D0
            ),
            "accommodation_supplement_weekly_rent_received_from_other_residents": D0,
        }
        values = self._evaluate(
            entity="Family",
            entity_id=f"{scenario.id}:as:{decimal_text(weekly_wages)}",
            inputs=inputs,
            outputs=[AS_UNROUNDED_OUTPUT, AS_ROUNDED_OUTPUT],
        )
        return (
            scalar_decimal(values, AS_UNROUNDED_OUTPUT),
            scalar_decimal(values, AS_ROUNDED_OUTPUT),
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
        best_start = self.best_start_total(
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
        as_unrounded, as_rounded = self.accommodation_values(
            scenario=scenario,
            weekly_wages=weekly_wages,
            net_benefit=net_benefit,
            eldest_ftc_annual=self.ftc_eldest_annual,
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
            "AS_Amount": as_unrounded,
            "WFF_abated": wff,
            "Net_Income": net_income,
            "Net_Income_annual": net_income * WEEKS_IN_MODEL_YEAR,
            "AS_Amount_statutory_rounded": as_rounded,
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
    required_wages = set(EXPECTED_SAMPLE_WAGES)
    required_wages.add(1499)
    required_wages.update(
        wage + 1 for wage in EXPECTED_SAMPLE_WAGES if wage < 1500
    )
    states = {
        wage: evaluator.evaluate_state(scenario, Decimal(wage))
        for wage in sorted(required_wages)
    }
    baseline = scalar_decimal(states[0], "Net_Income")
    sampled: dict[int, dict[str, Decimal | str | None]] = {}
    for wage in EXPECTED_SAMPLE_WAGES:
        state: dict[str, Decimal | str | None] = dict(states[wage])
        if wage == 1500:
            current = scalar_decimal(states[1499], "Net_Income")
            following = scalar_decimal(states[1500], "Net_Income")
        else:
            current = scalar_decimal(states[wage], "Net_Income")
            following = scalar_decimal(states[wage + 1], "Net_Income")
        state["EMTR"] = D1 - (following - current)
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
