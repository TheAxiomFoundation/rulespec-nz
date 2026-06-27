"""Phase 2: Extract rule names from all RuleSpec YAML files and update the inventory.

Usage: python scripts/phase2_extract_rules.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import yaml

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"


def canonical_rule_id(path_str: str, rule_name: str) -> str:
    """Generate a stable identifier for a rule in a module."""
    path_obj = Path(path_str)
    prefix = path_obj.parts[0]
    target = Path(*path_obj.parts[1:]).with_suffix("").as_posix()
    return f"{prefix}:{target}#{rule_name}"


def extract_rules(path: Path) -> list[dict[str, Any]]:
    """Extract rule metadata from a RuleSpec YAML file."""
    payload = cast(dict[str, Any], yaml.safe_load(path.read_text()) or {})
    rules = cast(list[dict[str, Any]], payload.get("rules") or [])
    result: list[dict[str, Any]] = []
    for rule in rules:
        if not isinstance(rule, dict) or not rule.get("name"):
            continue
        name = str(rule["name"])
        kind = str(rule.get("kind", "unknown"))
        source = str(rule.get("source", ""))
        result.append({
            "id": canonical_rule_id(path.relative_to(ROOT).as_posix(), name),
            "name": name,
            "kind": kind,
            "source_family": _infer_source_family(source, kind),
        })
    return result


def _infer_source_family(source: str, kind: str) -> str:
    """Infer source family from the rule's source string and kind."""
    source_lower = source.lower()
    if "accident compensation" in source_lower:
        return "acc_earners_levy"
    if "goods and services tax act" in source_lower:
        return "gst"
    if "income tax act" in source_lower or "ird" in source_lower:
        return "income_tax"
    if "kiwisaver act" in source_lower:
        return "kiwisaver"
    if "social security act" in source_lower or "social security regulations" in source_lower:
        if "accommodation" in source_lower:
            return "accommodation_supplement"
        if "childcare" in source_lower:
            return "childcare_assistance"
        if "child_disability" in source_lower or "child disability" in source_lower:
            return "child_disability_allowance"
        if "disability" in source_lower:
            return "disability_allowance"
        if "winter" in source_lower:
            return "winter_energy_payment"
        return "social_security_main_benefits"
    if "new zealand superannuation" in source_lower or "nz super" in source_lower:
        return "nz_superannuation"
    if "health entitlement" in source_lower or "community services card" in source_lower:
        return "community_services_card"
    if kind == "derived":
        return "computed"
    return "statutory_parameter"


def load_inventory() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig")))


def update_inventory() -> None:
    """Read inventory, add rules extraction to each module, save."""
    inventory = load_inventory()
    existing_paths = {m["path"] for m in inventory["modules"]}
    all_yaml_paths = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "nz").rglob("*.yaml")
        if not p.name.endswith(".test.yaml")
    )

    # Add any missing modules (e.g., the new deferred ones)
    for path_str in all_yaml_paths:
        if path_str not in existing_paths:
            p = ROOT / path_str
            payload = cast(dict[str, Any], yaml.safe_load(p.read_text()) or {})
            mod = cast(dict[str, Any], payload.get("module", {}))
            inventory["modules"].append({
                "path": path_str,
                "surface_ids": [path_str.replace("/", "-").replace(".yaml", "")],
                "source_families": [mod.get("summary", "deferred module")[:60]],
                "authority": "official_nz_legislation",
                "source_route": "pco_bulk_xml_extract",
                "oracle_links": cast(list[str], mod.get("source_verification", {}).get("oracle_links", [])),
                "triangulation_status": "inventory_seeded",
            })
            existing_paths.add(path_str)

    # Add rules extraction to each module
    for module in inventory["modules"]:
        path = ROOT / module["path"]
        if path.exists():
            rules = extract_rules(path)
            module["rules"] = rules
        else:
            module["rules"] = []

    # Update status
    inventory["module_inventory_status"] = "rule_level_complete"
    inventory["generated_at"] = "2026-06-25"

    with open(INVENTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=4, ensure_ascii=False)

    print(f"Updated {INVENTORY_PATH}")
    print(f"Total modules: {len(inventory['modules'])}")
    total_rules = sum(len(m.get("rules", [])) for m in inventory["modules"])
    print(f"Total rules extracted: {total_rules}")


if __name__ == "__main__":
    update_inventory()
