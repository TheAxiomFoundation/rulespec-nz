import sys
from pathlib import Path

import pytest

# Ensure scripts can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.phase2_extract_rules import canonical_rule_id


@pytest.mark.parametrize(
    "path_str,rule_name,expected",
    [
        # Standard paths with extensions
        ("nz/social_security/benefit.yaml", "my_rule", "nz:social_security/benefit#my_rule"),
        ("nz/income_tax.yaml", "tax_rate", "nz:income_tax#tax_rate"),
        # Deeper paths
        ("nz/a/b/c/d/file.yaml", "deep_rule", "nz:a/b/c/d/file#deep_rule"),
        # Paths without extensions
        ("nz/social_security/benefit", "my_rule", "nz:social_security/benefit#my_rule"),
        ("nz/income_tax", "tax_rate", "nz:income_tax#tax_rate"),
        # Other extensions
        ("nz/data.json", "json_rule", "nz:data#json_rule"),
    ],
)
def test_canonical_rule_id_happy_paths(path_str: str, rule_name: str, expected: str) -> None:
    """Test generating a stable identifier for a rule."""
    assert canonical_rule_id(path_str, rule_name) == expected


@pytest.mark.parametrize(
    "path_str,expected_match",
    [
        ("", "Path string must have at least two parts"),
        ("file.yaml", "Path string must have at least two parts"),
        ("only_one_part", "Path string must have at least two parts"),
        ("/", "Path string must be relative"),
        ("/nz/social_security/benefit.yaml", "Path string must be relative"),
    ]
)
def test_canonical_rule_id_edge_cases(path_str: str, expected_match: str) -> None:
    """Test ValueError is raised for invalid or absolute paths."""
    with pytest.raises(ValueError, match=expected_match):
        canonical_rule_id(path_str, "my_rule")
