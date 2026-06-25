from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

from pathlib import Path
from typing import Any, cast

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
KIWISAVER_RULESPEC_PATH = ROOT / "nz" / "statutes" / "kiwisaver" / "contributions.yaml"
KIWISAVER_TEST_PATH = ROOT / "nz" / "statutes" / "kiwisaver" / "contributions.test.yaml"
YamlMap = dict[str, Any]


def load_yaml(path: Path) -> YamlMap:
    return cast(YamlMap, yaml.safe_load(path.read_text(encoding="utf-8")))


@pytest.mark.integration
def test_kiwisaver_rulespec_records_official_sources_and_policyengine_boundary() -> (
    None
):
    rulespec = load_yaml(KIWISAVER_RULESPEC_PATH)
    source = rulespec["module"]["source_verification"]

    assert rulespec["format"] == "rulespec/v1"
    assert "PolicyEngine NZ is" in rulespec["module"]["summary"]
    assert "supporting-reference discovery" in rulespec["module"]["summary"]
    assert (
        "nz/statute/act/public/2006/0040/section/64" in source["corpus_citation_paths"]
    )
    assert (
        "nz/statute/act/public/2006/0040/section/101B"
        in source["corpus_citation_paths"]
    )
    assert (
        "nz/agency/ird/kiwisaver-contribution-rates" in source["corpus_citation_paths"]
    )


@pytest.mark.integration
def test_kiwisaver_rulespec_contains_expected_rate_progression() -> None:
    rulespec = load_yaml(KIWISAVER_RULESPEC_PATH)
    rules = {rule["name"]: rule for rule in rulespec["rules"]}

    employee_rates = rules["kiwisaver_employee_minimum_contribution_rate"]["versions"]
    employer_rates = rules["kiwisaver_employer_minimum_contribution_rate"]["versions"]

    assert employee_rates[-2:] == [
        {"effective_from": "2026-04-01", "formula": "0.035"},
        {"effective_from": "2028-04-01", "formula": "0.04"},
    ]
    assert employer_rates[-2:] == [
        {"effective_from": "2026-04-01", "formula": "0.035"},
        {"effective_from": "2028-04-01", "formula": "0.04"},
    ]
    assert rules["kiwisaver_government_contribution_match_rate"]["versions"] == [
        {"effective_from": "2025-07-01", "formula": "0.25"}
    ]


@pytest.mark.integration
def test_kiwisaver_companion_tests_cover_minimums_cap_and_negative_income() -> None:
    cases = cast(
        list[YamlMap], yaml.safe_load(KIWISAVER_TEST_PATH.read_text(encoding="utf-8"))
    )
    names = {case["name"] for case in cases}

    assert names == {
        "employee_and_employer_minimum_rates_2026",
        "government_contribution_cap_from_threshold",
        "negative_salary_does_not_create_contributions",
    }

    cap_case = next(
        case
        for case in cases
        if case["name"] == "government_contribution_cap_from_threshold"
    )
    assert (
        cap_case["output"][
            "nz:statutes/kiwisaver/contributions#kiwisaver_government_contribution_maximum"
        ]
        == 260.72
    )
