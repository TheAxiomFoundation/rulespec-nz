import pytest
from pathlib import Path
import scripts.phase2_extract_rules as p2
from scripts.phase2_extract_rules import canonical_rule_id, extract_rules, _infer_source_family

def test_canonical_rule_id():
    assert canonical_rule_id("nz/statutes/test.yaml", "rule_1") == "nz:statutes/test#rule_1"
    assert canonical_rule_id("nz/regulations/some_file.yaml", "another_rule") == "nz:regulations/some_file#another_rule"
    # Ensure it works correctly with a deeper path
    assert canonical_rule_id("nz/policies/deep/dir/test.yaml", "deep_rule") == "nz:policies/deep/dir/test#deep_rule"

def test_infer_source_family():
    # Happy paths based on exact matches
    assert _infer_source_family("Accident Compensation Act", "statutory") == "acc_earners_levy"
    assert _infer_source_family("Goods and Services Tax Act", "statutory") == "gst"
    assert _infer_source_family("Income Tax Act 2007", "statutory") == "income_tax"
    assert _infer_source_family("IRD guide", "statutory") == "income_tax"
    assert _infer_source_family("KiwiSaver Act 2006", "statutory") == "kiwisaver"

    # Social Security main benefits fallback
    assert _infer_source_family("Social Security Act 2018", "statutory") == "social_security_main_benefits"

    # Social Security sub-benefits
    assert _infer_source_family("Social Security Act - Accommodation Supplement", "statutory") == "accommodation_supplement"
    assert _infer_source_family("Social Security Act - Childcare Assistance", "statutory") == "childcare_assistance"
    assert _infer_source_family("Social Security Act - Child Disability Allowance", "statutory") == "child_disability_allowance"
    assert _infer_source_family("Social Security Act - Disability Allowance", "statutory") == "disability_allowance"
    assert _infer_source_family("Social Security Act - Winter Energy Payment", "statutory") == "winter_energy_payment"

    # NZ Super
    assert _infer_source_family("New Zealand Superannuation Act", "statutory") == "nz_superannuation"
    assert _infer_source_family("NZ Super", "statutory") == "nz_superannuation"

    # Community services
    assert _infer_source_family("Health Entitlement", "statutory") == "community_services_card"
    assert _infer_source_family("Community Services Card", "statutory") == "community_services_card"

    # Fallbacks based on kind
    assert _infer_source_family("Unknown Source", "derived") == "computed"
    assert _infer_source_family("Unknown Source", "statutory") == "statutory_parameter"


def test_extract_rules_happy_path(tmp_path, monkeypatch):
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
    assert result[1]["kind"] == "unknown"  # Default when 'kind' is missing
    assert result[1]["source_family"] == "acc_earners_levy"

def test_extract_rules_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "empty.yaml"
    yaml_file.write_text("")

    result = extract_rules(yaml_file)
    assert result == []

def test_extract_rules_no_rules_key(tmp_path, monkeypatch):
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "no_rules.yaml"
    yaml_file.write_text("module:\n  summary: Only module info")

    result = extract_rules(yaml_file)
    assert result == []

def test_extract_rules_rules_is_not_a_list(tmp_path, monkeypatch):
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "bad_rules.yaml"
    yaml_file.write_text("rules: This is not a list")

    result = extract_rules(yaml_file)
    assert result == []

def test_extract_rules_payload_is_not_a_dict(tmp_path, monkeypatch):
    monkeypatch.setattr(p2, "ROOT", tmp_path)
    nz_dir = tmp_path / "nz"
    nz_dir.mkdir()
    yaml_file = nz_dir / "list.yaml"
    yaml_file.write_text("- item1\n- item2")

    result = extract_rules(yaml_file)
    assert result == []

def test_extract_rules_skip_invalid_rules(tmp_path, monkeypatch):
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
