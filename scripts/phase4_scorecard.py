"""Phase 4: Generate a compact completion scorecard from the RuleSpec rule inventory.

Usage: python scripts/phase4_scorecard.py
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"
SCORECARD_PATH = ROOT / "data" / "coverage" / "rulespec-scorecard.json"


def generate_scorecard() -> dict[str, Any]:
    inventory = cast(
        dict[str, Any], json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    )
    modules = cast(list[dict[str, Any]], inventory["modules"])
    clusters = cast(list[dict[str, Any]], inventory["duplicate_clusters"])

    total_modules = len(modules)
    modules_with_rules = sum(1 for m in modules if m.get("rules"))
    modules_deferred = sum(
        1 for m in modules if not m.get("rules") or len(m.get("rules", [])) == 0
    )
    total_rules = sum(len(m.get("rules", [])) for m in modules)

    total_clusters = len(clusters)
    total_conflicts = sum(len(c.get("conflicts", [])) for c in clusters)
    resolved = sum(
        1 for c in clusters for cf in c.get("conflicts", [])
        if cf.get("status") == "resolved_official_source"
    )
    unresolved = sum(
        1 for c in clusters for cf in c.get("conflicts", [])
        if cf.get("status") == "unresolved"
    )

    # Build status view
    encoded = sorted(
        m["path"] for m in modules if m.get("rules") and len(m.get("rules", [])) > 0
    )
    deferred = sorted(
        m["path"]
        for m in modules
        if not m.get("rules") or len(m.get("rules", [])) == 0
    )
    # Check for blocked modules (none currently)
    blocked: list[str] = []

    scorecard: dict[str, Any] = {
        "generated_at": str(date.today()),
        "jurisdiction": "nz",
        "purpose": "Compact completion scorecard for RuleSpec rule inventory and triangulation",
        "total_modules": total_modules,
        "modules_with_rules": modules_with_rules,
        "modules_deferred": modules_deferred,
        "total_rules": total_rules,
        "total_duplicate_clusters": total_clusters,
        "total_conflicts": total_conflicts,
        "resolved_conflicts": resolved,
        "unresolved_conflicts": unresolved,
        "status_view": {
            "encoded": encoded,
            "deferred": deferred,
            "blocked": blocked,
        },
    }

    SCORECARD_PATH.write_text(
        json.dumps(scorecard, indent=4, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Scorecard written to {SCORECARD_PATH}")
    print(f"  Modules: {total_modules} ({modules_with_rules} with rules, {modules_deferred} deferred)")
    print(f"  Rules extracted: {total_rules}")
    print(f"  Duplicate clusters: {total_clusters}")
    print(f"  Conflicts: {total_conflicts} (resolved: {resolved}, unresolved: {unresolved})")
    print(f"  Status view: encoded={len(encoded)}, deferred={len(deferred)}, blocked={len(blocked)}")

    return scorecard


if __name__ == "__main__":
    generate_scorecard()