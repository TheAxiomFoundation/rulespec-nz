from pathlib import Path

import pytest

import scripts.phase2_extract_rules as p2
from scripts.phase2_extract_rules import (
    _infer_source_family,
    canonical_rule_id,
    extract_rules,
)
from scripts.rulespec_layout import ATOMIC_CONTENT_ROOTS, atomic_rulespec_paths


def test_canonical_rule_id() -> None:
    assert (
        canonical_rule_id("nz/statutes/test.yaml", "rule_1")
        == "nz:statutes/test#rule_1"
    )
    assert (
        canonical_rule_id("nz/regulations/some_file.yaml", "another_rule")
        == "nz:regulations/some_file#another_rule"
    )
    assert (
        canonical_rule_id("nz/policies/deep/dir/test.yaml", "deep_rule")
        == "nz:policies/deep/dir/test#deep_rule"
    )


def test_inventory_discovery_uses_only_four_atomic_exact_yaml_roots(
    tmp_path: Path,
) -> None:
    expected: list[Path] = []
    for source_root in ATOMIC_CONTENT_ROOTS:
        module = tmp_path / "nz" / source_root / "example.yaml"
        module.parent.mkdir(parents=True)
        module.write_text("format: rulespec/v1\n")
        module.with_name("example.test.yaml").write_text("[]\n")
        expected.append(module)

    program = tmp_path / "nz" / "programs" / "example" / "fy-2026.yaml"
    program.parent.mkdir(parents=True)
    program.write_text("program: nz/example\n")

    assert atomic_rulespec_paths(tmp_path) == tuple(sorted(expected))


def test_inventory_discovery_rejects_removed_yml_spelling(tmp_path: Path) -> None:
    legacy_yml = tmp_path / "nz" / "statutes" / "legacy.yml"
    legacy_yml.parent.mkdir(parents=True)
    legacy_yml.write_text("format: rulespec/v1\n")

    with pytest.raises(ValueError, match="exact \\.yaml"):
        atomic_rulespec_paths(tmp_path)


def test_inventory_discovery_rejects_aliases(tmp_path: Path) -> None:
    module = tmp_path / "outside.yaml"
    module.write_text("format: rulespec/v1\n")
    alias = tmp_path / "nz" / "statutes" / "alias.yaml"
    alias.parent.mkdir(parents=True)
    alias.symlink_to(module)

    with pytest.raises(ValueError, match="must not be an alias"):
        atomic_rulespec_paths(tmp_path)


@pytest.mark.parametrize(
    ("source", "kind", "expected"),
    [
        ("Accident Compensation Act 2001", "parameter", "acc_earners_levy"),
        ("ACCIDENT COMPENSATION", "unknown", "acc_earners_levy"),
        ("Goods and Services Tax Act 1985", "parameter", "gst"),
        ("Income Tax Act 2007", "parameter", "income_tax"),
        ("IRD data", "derived", "income_tax"),
        ("KiwiSaver Act 2006", "parameter", "kiwisaver"),
        ("Social Security Act 2018", "parameter", "social_security_main_benefits"),
        ("Social Security Regulations", "parameter", "social_security_main_benefits"),
        (
            "Social Security Act - Accommodation",
            "parameter",
            "accommodation_supplement",
        ),
        ("Social Security Act - Childcare", "parameter", "childcare_assistance"),
        (
            "Social Security Act - child_disability",
            "parameter",
            "child_disability_allowance",
        ),
        (
            "Social Security Act - Child Disability",
            "parameter",
            "child_disability_allowance",
        ),
        ("Social Security Act - Disability", "parameter", "disability_allowance"),
        ("Social Security Act - Winter", "parameter", "winter_energy_payment"),
        (
            "New Zealand Superannuation and Retirement Income Act 2001",
            "parameter",
            "nz_superannuation",
        ),
        ("NZ Super", "parameter", "nz_superannuation"),
        (
            "Health Entitlement Cards Regulations",
            "parameter",
            "community_services_card",
        ),
        ("Community Services Card", "parameter", "community_services_card"),
        ("Some other source", "derived", "computed"),
        ("Some other source", "parameter", "statutory_parameter"),
        ("", "parameter", "statutory_parameter"),
        ("", "derived", "computed"),
        ("Unknown Source", "unknown", "statutory_parameter"),
    ],
)
def test_infer_source_family(source: str, kind: str, expected: str) -> None:
    assert _infer_source_family(source, kind) == expected


def test_extract_rules_happy_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "test.yaml"

    yaml_content = """
module:
  summary: Test module
rules:
  - name: test_rule_1
    kind: derived
    source: income tax act
  - name: test_rule_2
    source: accident compensation
"""
    yaml_file.write_text(yaml_content)

    result = extract_rules(yaml_file)

    assert len(result) == 2
    assert result[0]["id"] == "nz:test#test_rule_1"
    assert result[0]["name"] == "test_rule_1"
    assert result[0]["kind"] == "derived"
    assert result[0]["source_family"] == "income_tax"
    assert result[1]["id"] == "nz:test#test_rule_2"
    assert result[1]["name"] == "test_rule_2"
    assert result[1]["kind"] == "unknown"
    assert result[1]["source_family"] == "acc_earners_levy"


def test_extract_rules_empty_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "empty.yaml"
    yaml_file.write_text("")

    assert extract_rules(yaml_file) == []


def test_extract_rules_no_rules_key(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "no_rules.yaml"
    yaml_file.write_text("module:\n  summary: Only module info")

    assert extract_rules(yaml_file) == []


def test_extract_rules_rules_is_not_a_list(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "bad_rules.yaml"
    yaml_file.write_text("rules: This is not a list")

    assert extract_rules(yaml_file) == []


def test_extract_rules_payload_is_not_a_dict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "list.yaml"
    yaml_file.write_text("- item1\n- item2")

    assert extract_rules(yaml_file) == []


def test_extract_rules_skip_invalid_rules(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "invalid_rules.yaml"

    yaml_content = """
rules:
  - "Not a dict"
  - name: valid_rule
  - kind: derived # Missing name
  - name: "" # Empty name
"""
    yaml_file.write_text(yaml_content)

    result = extract_rules(yaml_file)

    assert len(result) == 1
    assert result[0]["name"] == "valid_rule"
    assert result[0]["id"] == "nz:invalid_rules#valid_rule"
