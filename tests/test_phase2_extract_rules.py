import pytest
from scripts.phase2_extract_rules import canonical_rule_id


@pytest.mark.parametrize(
    ("path_str", "rule_name", "expected"),
    [
        # Standard path with directory and file
        (
            "nz/statutes/income_tax_act.yaml",
            "my_rule",
            "nz:statutes/income_tax_act#my_rule",
        ),
        # Path with multiple subdirectories
        ("nz/dir1/dir2/file.yaml", "rule", "nz:dir1/dir2/file#rule"),
        # Path without an extension
        ("nz/statutes/income_tax_act", "my_rule", "nz:statutes/income_tax_act#my_rule"),
        # Empty rule name
        ("nz/file.yaml", "", "nz:file#"),
        # Other prefix
        ("au/statutes/income_tax.yaml", "rule1", "au:statutes/income_tax#rule1"),
    ],
)
def test_canonical_rule_id_happy_paths(path_str: str, rule_name: str, expected: str):
    """Test canonical_rule_id with standard valid inputs."""
    assert canonical_rule_id(path_str, rule_name) == expected


def test_canonical_rule_id_single_component():
    """Test that a single component path raises ValueError due to empty target."""
    with pytest.raises(ValueError, match="has an empty name"):
        canonical_rule_id("file.yaml", "rule")


def test_canonical_rule_id_empty_path():
    """Test that an empty path raises IndexError because there's no first part."""
    with pytest.raises(IndexError):
        canonical_rule_id("", "rule")
