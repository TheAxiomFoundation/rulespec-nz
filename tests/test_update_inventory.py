import pytest
from _update_inventory import extract_rule_info

class MockPath:
    def __init__(self, content: str):
        self._content = content

    def read_text(self, encoding="utf-8"):
        return self._content

def test_extract_rule_info_all_fields():
    yaml_content = """
rules:
  - name: my_rule
    kind: constant
    source_family: custom_source
"""
    path = MockPath(yaml_content)
    result = extract_rule_info(path, "nz/module/test.yaml")

    assert len(result) == 1
    assert result[0] == {
        "id": "nz:module/test#my_rule",
        "name": "my_rule",
        "kind": "constant",
        "source_family": "custom_source",
    }

def test_extract_rule_info_defaults():
    yaml_content = """
rules:
  - name: minimal_rule
"""
    path = MockPath(yaml_content)
    # Using a path with multiple slashes to ensure target/source_family parsing is correct
    rel_path = "nz/category/subcategory/rule_def.yaml"
    result = extract_rule_info(path, rel_path)

    assert len(result) == 1
    assert result[0] == {
        "id": "nz:category/subcategory/rule_def#minimal_rule",
        "name": "minimal_rule",
        "kind": "parameter",  # Default kind
        "source_family": "rule_def",  # Parsed from filename without .yaml
    }

def test_extract_rule_info_ignores_non_dict():
    yaml_content = """
rules:
  - name: valid_rule
  - "this is a string, not a dict, so it should be ignored"
  - null
"""
    path = MockPath(yaml_content)
    result = extract_rule_info(path, "nz/test.yaml")

    assert len(result) == 1
    assert result[0]["name"] == "valid_rule"

def test_extract_rule_info_empty_rules():
    yaml_content = """
module:
  source_verification: {}
"""
    path = MockPath(yaml_content)
    result = extract_rule_info(path, "nz/test.yaml")

    assert result == []
