"""Script to add new RuleSpec modules to the rule inventory."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"
SCORECARD_PATH = ROOT / "data" / "coverage" / "rulespec-scorecard.json"


def extract_rule_info(payload, rel_path):
    rules = payload.get("rules", [])
    result = []
    for r in rules:
        if not isinstance(r, dict):
            continue
        name = r.get("name", "")
        kind = r.get("kind", "parameter")
        source_family = r.get("source_family", "")
        if not source_family:
            source_family = rel_path.replace(".yaml", "").split("/")[-1]
        prefix = rel_path.split("/")[0]
        target = "/".join(rel_path.replace(".yaml", "").split("/")[1:])
        stable_id = f"{prefix}:{target}#{name}"
        result.append({
            "id": stable_id,
            "name": name,
            "kind": kind,
            "source_family": source_family,
        })
    return result


def main():
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    existing_paths = {m["path"] for m in inventory["modules"]}

    all_yaml = sorted(
        p.relative_to(ROOT).as_posix()
        for p in (ROOT / "nz").rglob("*.yaml")
        if not p.name.endswith(".test.yaml")
    )

    added = 0
    for rel_path in all_yaml:
        if rel_path in existing_paths:
            continue
        path = ROOT / rel_path
        if not path.exists():
            continue

        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        payload = payload or {}
        rules = extract_rule_info(payload, rel_path)
        sv = payload.get("module", {}).get("source_verification", {})
        corpus_paths = sv.get("corpus_citation_paths", [])
        if corpus_paths:
            authority = "official_nz_legislation"
            source_route = "pco_bulk_xml_extract"
        else:
            authority = "official_agency_table"
            source_route = "official_agency_table"

        entry = {
            "path": rel_path,
            "surface_ids": [rel_path.replace(".yaml", "")],
            "source_families": [rel_path.replace(".yaml", "").replace("/", "_")],
            "authority": authority,
            "source_route": source_route,
            "oracle_links": ["nztaxmicrosim", "openfisca-aotearoa", "policyengine-nz"],
            "triangulation_status": "inventory_seeded",
            "rules": rules,
        }
        inventory["modules"].append(entry)
        print(f"Added: {rel_path} ({len(rules)} rules)")
        added += 1

    INVENTORY_PATH.write_text(
        json.dumps(inventory, indent=4, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nInventory: {len(inventory['modules'])} modules ({added} new)")

    if SCORECARD_PATH.exists():
        sc = json.loads(SCORECARD_PATH.read_text(encoding="utf-8-sig"))
        sc["total_modules"] = len(inventory["modules"])
        sc["modules_with_rules"] = sum(1 for m in inventory["modules"] if m.get("rules"))
        sc["total_rules"] = sum(len(m.get("rules", [])) for m in inventory["modules"])
        SCORECARD_PATH.write_text(
            json.dumps(sc, indent=4, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Scorecard: {sc['total_modules']} modules, {sc['total_rules']} rules")


if __name__ == "__main__":
    main()