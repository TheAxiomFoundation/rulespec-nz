from __future__ import annotations

import pytest

from scripts.phase2_extract_rules import _infer_source_family


@pytest.mark.parametrize(
    ("source", "kind", "expected"),
    [
        # ACC
        ("Accident Compensation Act 2001", "parameter", "acc_earners_levy"),
        ("ACCIDENT COMPENSATION", "unknown", "acc_earners_levy"),

        # GST
        ("Goods and Services Tax Act 1985", "parameter", "gst"),

        # Income Tax
        ("Income Tax Act 2007", "parameter", "income_tax"),
        ("IRD data", "derived", "income_tax"),

        # KiwiSaver
        ("KiwiSaver Act 2006", "parameter", "kiwisaver"),

        # Social Security
        ("Social Security Act 2018", "parameter", "social_security_main_benefits"),
        ("Social Security Regulations", "parameter", "social_security_main_benefits"),
        ("Social Security Act - Accommodation", "parameter", "accommodation_supplement"),
        ("Social Security Act - Childcare", "parameter", "childcare_assistance"),
        ("Social Security Act - child_disability", "parameter", "child_disability_allowance"),
        ("Social Security Act - Child Disability", "parameter", "child_disability_allowance"),
        ("Social Security Act - Disability", "parameter", "disability_allowance"),
        ("Social Security Act - Winter", "parameter", "winter_energy_payment"),

        # NZ Super
        ("New Zealand Superannuation and Retirement Income Act 2001", "parameter", "nz_superannuation"),
        ("NZ Super", "parameter", "nz_superannuation"),

        # Community Services Card
        ("Health Entitlement Cards Regulations", "parameter", "community_services_card"),
        ("Community Services Card", "parameter", "community_services_card"),

        # Fallbacks based on kind
        ("Some other source", "derived", "computed"),
        ("Some other source", "parameter", "statutory_parameter"),
        ("", "parameter", "statutory_parameter"),
        ("", "derived", "computed"),
        ("Unknown Source", "unknown", "statutory_parameter"),
    ],
)
def test_infer_source_family(source: str, kind: str, expected: str) -> None:
    """Test the extraction of source family from source and kind strings."""
    assert _infer_source_family(source, kind) == expected
