"""Phase 3: Add reconciliation surface links, conflict declarations, and official-source
decisions to duplicate clusters in the RuleSpec rule inventory.

Usage: python scripts/phase3_reconciliation_workflow.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"

CLUSTER_SURFACE_LINKS: dict[str, list[dict[str, str]]] = {
    "income-tax-rate-schedule": [
        {"oracle_id": "policyengine-nz", "surface_id": "income-tax"},
        {"oracle_id": "openfisca-aotearoa", "surface_id": "income-tax-and-family-scheme"},
        {"oracle_id": "nztaxmicrosim", "surface_id": "personal-income-tax-history"},
    ],
    "acc-earners-levy": [
        {"oracle_id": "policyengine-nz", "surface_id": "acc-earners-levy"},
        {"oracle_id": "openfisca-aotearoa", "surface_id": "acc-compensation-earners-levy"},
        {"oracle_id": "nztaxmicrosim", "surface_id": "acc-earners-levy"},
    ],
    "working-for-families": [
        {"oracle_id": "policyengine-nz", "surface_id": "working-for-families"},
        {"oracle_id": "openfisca-aotearoa", "surface_id": "income-tax-and-family-scheme"},
        {"oracle_id": "nztaxmicrosim", "surface_id": "working-for-families"},
    ],
    "main-benefits": [
        {"oracle_id": "policyengine-nz", "surface_id": "main-benefits-jobseeker"},
        {"oracle_id": "openfisca-aotearoa", "surface_id": "social-security-main-benefits"},
        {"oracle_id": "nztaxmicrosim", "surface_id": "main-benefits-and-supplements"},
    ],
    "nz-superannuation": [
        {"oracle_id": "policyengine-nz", "surface_id": "new-zealand-superannuation"},
        {"oracle_id": "openfisca-aotearoa", "surface_id": "social-security-main-benefits"},
        {"oracle_id": "nztaxmicrosim", "surface_id": "main-benefits-and-supplements"},
    ],
}

CLUSTER_CONFLICTS: dict[str, list[dict[str, str]]] = {
    "income-tax-rate-schedule": [
        {
            "type": "value_mismatch",
            "status": "resolved_official_source",
            "description": "PolicyEngine NZ uses inflation-adjusted 2024/25 placeholder "
            "rates instead of current Schedule 1 rates",
            "official_source_decision": "Official Schedule 1 of Income Tax Act 2007 "
            "prevails; oracle placeholder rates are excluded from canonical encoding",
        },
    ],
    "acc-earners-levy": [
        {
            "type": "value_mismatch",
            "status": "resolved_official_source",
            "description": "PolicyEngine NZ levy rates and caps lag behind current "
            "regulations by 1-2 years",
            "official_source_decision": "Official Accident Compensation (Earners' Levy) "
            "Regulations 2025 prevail; oracle stale values are comparison-only",
        },
    ],
    "working-for-families": [
        {
            "type": "value_mismatch",
            "status": "resolved_official_source",
            "description": "Oracle WFF placeholder values exist in nztaxmicrosim and may "
            "not reflect current legislation",
            "official_source_decision": "Official Income Tax Act 2007 subpart MA, MF, "
            "and ME provisions prevail; oracle placeholder values excluded",
        },
        {
            "type": "scope_mismatch",
            "status": "resolved_official_source",
            "description": "nztaxmicrosim applies simplified family scheme thresholds "
            "that do not match all statutory area categories",
            "official_source_decision": "Statutory area categories in Schedule 14 of "
            "Income Tax Act 2007 are canonical; oracle simplified scope is comparison-only",
        },
    ],
    "main-benefits": [
        {
            "type": "value_mismatch",
            "status": "resolved_official_source",
            "description": "OpenFisca Aotearoa and PolicyEngine NZ benefit rates encoded "
            "in older Python formulas may diverge from current Schedule 4 rates",
            "official_source_decision": "Official Social Security Act 2018 Schedule 4 "
            "Part 1-7 rates and Social Security Regulations 2018 rates prevail; "
            "oracle fixtures are historical reference only",
        },
        {
            "type": "stale_oracle",
            "status": "unresolved",
            "description": "OpenFisca Aotearoa commit 76062ffc may be stale against "
            "live official rates; follow-on pin reconciliation required",
        },
    ],
    "nz-superannuation": [
        {
            "type": "value_mismatch",
            "status": "resolved_official_source",
            "description": "OpenFisca Aotearoa and PolicyEngine NZ superannuation "
            "eligibility logic uses legacy MSD thresholds",
            "official_source_decision": "Official New Zealand Superannuation and "
            "Retirement Income Act 2001 and MSD current rate tables prevail; "
            "oracle comparison only",
        },
    ],
}


def update_clusters() -> None:
    """Add reconciliation surface links, conflicts, and official-source decisions."""
    inventory = cast(
        dict[str, Any], json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    )
    clusters = cast(list[dict[str, Any]], inventory["duplicate_clusters"])

    for cluster in clusters:
        cid = str(cluster["id"])
        cluster["reconciliation_surface_links"] = CLUSTER_SURFACE_LINKS.get(cid, [])
        cluster["conflicts"] = CLUSTER_CONFLICTS.get(cid, [])
        cluster["reconciliation_status"] = "triangulated_with_conflicts"

    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4, ensure_ascii=False)

    total = len(clusters)
    total_cf = sum(len(c.get("conflicts", [])) for c in clusters)
    resolved = sum(
        1 for c in clusters for cf in c.get("conflicts", [])
        if cf.get("status") == "resolved_official_source"
    )
    unresolved = sum(
        1 for c in clusters for cf in c.get("conflicts", [])
        if cf.get("status") == "unresolved"
    )
    print(f"Updated {INVENTORY_PATH}")
    print(f"Clusters: {total}, Conflicts: {total_cf}, Resolved: {resolved}, Unresolved: {unresolved}")


if __name__ == "__main__":
    update_clusters()