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

