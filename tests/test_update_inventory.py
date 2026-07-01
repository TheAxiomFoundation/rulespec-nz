from _update_inventory import extract_rule_info


def test_extract_rule_info_all_fields():
    payload = {
        "rules": [
            {
                "name": "my_rule",
                "kind": "constant",
                "source_family": "custom_source",
            },
        ],
    }
    result = extract_rule_info(payload, "nz/module/test.yaml")

    assert len(result) == 1
    assert result[0] == {
        "id": "nz:module/test#my_rule",
        "name": "my_rule",
        "kind": "constant",
        "source_family": "custom_source",
    }


def test_extract_rule_info_defaults():
    payload = {"rules": [{"name": "minimal_rule"}]}
    # Using a path with multiple slashes to ensure target/source_family parsing is correct
    rel_path = "nz/category/subcategory/rule_def.yaml"
    result = extract_rule_info(payload, rel_path)

    assert len(result) == 1
    assert result[0] == {
        "id": "nz:category/subcategory/rule_def#minimal_rule",
        "name": "minimal_rule",
        "kind": "parameter",  # Default kind
        "source_family": "rule_def",  # Parsed from filename without .yaml
    }


def test_extract_rule_info_ignores_non_dict():
    payload = {
        "rules": [
            {"name": "valid_rule"},
            "this is a string, not a dict, so it should be ignored",
            None,
        ],
    }
    result = extract_rule_info(payload, "nz/test.yaml")

    assert len(result) == 1
    assert result[0]["name"] == "valid_rule"


def test_extract_rule_info_empty_rules():
    payload = {"module": {"source_verification": {}}}
    result = extract_rule_info(payload, "nz/test.yaml")

    assert result == []
