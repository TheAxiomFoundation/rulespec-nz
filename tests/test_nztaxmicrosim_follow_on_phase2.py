"""Phase 2: Official-source Extraction Verification for nztaxmicrosim follow-on reconciliation.

Tests verify that each extraction unit identified in the manifest has a
corresponding RuleSpec YAML module with companion test file.
"""

from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXTRACTION_MANIFEST_PATH = (
    ROOT / "data" / "oracles" / "nztaxmicrosim-extraction-units.json"
)


def load_json(path: Path) -> dict:
    return dict(json.loads(path.read_text(encoding="utf-8-sig")))


def extraction_units() -> list[dict]:
    manifest = load_json(EXTRACTION_MANIFEST_PATH)
    return manifest["extraction_units"]


@pytest.mark.unit
def test_every_extraction_unit_has_rulespec_yaml() -> None:
    """Each extraction unit must have a corresponding RuleSpec YAML file at its target_path."""
    for unit in extraction_units():
        rulespec_path = ROOT / unit["target_path"]
        assert rulespec_path.exists(), (
            f"Missing RuleSpec YAML for {unit['surface_id']}: {rulespec_path}"
        )


@pytest.mark.unit
def test_every_extraction_unit_has_companion_test_file() -> None:
    """Each extraction unit must have a companion .test.yaml file alongside its RuleSpec YAML."""
    for unit in extraction_units():
        test_path = ROOT / unit["target_path"].replace(".yaml", ".test.yaml")
        assert test_path.exists(), (
            f"Missing test file for {unit['surface_id']}: {test_path}"
        )


@pytest.mark.unit
def test_every_rulespec_yaml_has_required_sections() -> None:
    """Verify each RuleSpec YAML contains format, module, units, and rules sections."""
    for unit in extraction_units():
        path = ROOT / unit["target_path"]
        content = path.read_text(encoding="utf-8")
        assert "format: rulespec/v1" in content, (
            f"{unit['target_path']} missing format declaration"
        )
        assert "module:" in content, f"{unit['target_path']} missing module section"
        assert "units:" in content, f"{unit['target_path']} missing units section"
        assert "rules:" in content, f"{unit['target_path']} missing rules section"


@pytest.mark.unit
def test_every_rulespec_yaml_has_source_verification() -> None:
    """Each RuleSpec YAML must have source_verification with corpus_citation_paths."""
    for unit in extraction_units():
        path = ROOT / unit["target_path"]
        content = path.read_text(encoding="utf-8")
        assert "source_verification:" in content, (
            f"{unit['target_path']} missing source_verification"
        )
        assert "corpus_citation_paths:" in content, (
            f"{unit['target_path']} missing corpus_citation_paths"
        )


@pytest.mark.unit
def test_every_rulespec_yaml_declares_nzd_unit() -> None:
    """Each RuleSpec YAML should declare NZD as a currency unit where applicable."""
    for unit in extraction_units():
        path = ROOT / unit["target_path"]
        content = path.read_text(encoding="utf-8")
        assert "NZD" in content, (
            f"{unit['target_path']} missing NZD currency unit declaration"
        )


@pytest.mark.unit
def test_every_extraction_unit_kind_matches_yaml_content() -> None:
    """Verify that each extraction unit's kind field aligns with the YAML content."""
    kind_check_map: dict[str, list[str]] = {
        "statutory_repayment_table": ["repayment", "student_loan"],
        "paye_deduction_aggregator": ["paye", "deduction"],
        "entitlement_and_rate_formula": ["ppl", "parental_leave", "entitlement"],
        "prescribed_investor_rate_tax": ["pir", "pie_"],
        "resident_withholding_tax_rate_table": ["rwt", "withholding"],
        "child_support_formula": ["cs_", "child_support"],
    }
    for unit in extraction_units():
        kind = unit["kind"]
        path = ROOT / unit["target_path"]
        content = path.read_text(encoding="utf-8").lower()
        keywords = kind_check_map.get(kind, [])
        if keywords:
            match_found = any(kw in content for kw in keywords)
            assert match_found, (
                f"{unit['target_path']} (kind={kind}) content mismatch: "
                f"no keywords {keywords} found in YAML"
            )


@pytest.mark.unit
def test_extraction_unit_target_paths_match_planned_rulespec_paths() -> None:
    """Verify that extraction unit target paths match the planned destinations in both source-map and inventory."""
    source_map_path = ROOT / "data" / "coverage" / "nztaxmicrosim-source-map.json"
    source_map = load_json(source_map_path)
    inventory_path = ROOT / "data" / "oracles" / "nztaxmicrosim-rule-inventory.json"
    inventory = load_json(inventory_path)
    inventory_surfaces = {s["id"]: s for s in inventory["rule_surfaces"]}

    for surface in source_map["surfaces"]:
        if not surface["implementation_status"].startswith("missing"):
            continue
        sid = surface["id"]
        planned = set(surface.get("planned_rulespec_paths", []))
        inv_surface = inventory_surfaces.get(sid, {})
        inv_planned = set(inv_surface.get("planned_destinations", []))
        assert planned == inv_planned, (
            f"{sid}: source-map paths {planned} != inventory paths {inv_planned}"
        )
        # Each extraction unit target_path should be in these sets
        for unit in extraction_units():
            if unit["surface_id"] == sid:
                assert unit["target_path"] in planned, (
                    f"{sid}: extraction unit target {unit['target_path']} not in planned paths {planned}"
                )
