from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import yaml


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"


def load_inventory() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig")))


def non_test_rulespec_paths() -> set[str]:
    return {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "nz").rglob("*.yaml")
        if not path.name.endswith(".test.yaml")
    }


def rulespec_rule_names(path: Path) -> list[dict[str, str]]:
    """Extract rule name and kind from a RuleSpec YAML file."""
    payload = cast(dict[str, Any], yaml.safe_load(path.read_text()) or {})
    rules = cast(list[dict[str, Any]], payload.get("rules") or [])
    return [
        {"name": str(rule["name"]), "kind": str(rule.get("kind", "unknown"))}
        for rule in rules
        if isinstance(rule, dict) and rule.get("name")
    ]


def canonical_rule_id(path_str: str, rule_name: str) -> str:
    """Generate a stable identifier for a rule in a module."""
    path_obj = Path(path_str)
    prefix = path_obj.parts[0]
    target = Path(*path_obj.parts[1:]).with_suffix("").as_posix()
    return f"{prefix}:{target}#{rule_name}"


def test_inventory_covers_every_rulespec_module() -> None:
    inventory = load_inventory()
    inventoried_paths = {module["path"] for module in inventory["modules"]}
    rulespec_paths = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "nz").rglob("*.yaml")
        if not path.name.endswith(".test.yaml")
    }
    assert inventoried_paths == rulespec_paths


def test_inventory_modules_record_authority_and_source_routes() -> None:
    inventory = load_inventory()
    authority_order = set(inventory["authority_order"])
    assert inventory["module_inventory_status"] in (
        "module_level_complete_rule_level_pending",
        "rule_level_complete",
    ), "module_inventory_status must be one of the valid states"
    assert (
        "Comparison oracles are never canonical law" in inventory["source_route_policy"]
    )
    for module in inventory["modules"]:
        assert (ROOT / module["path"]).exists(), module["path"]
        assert module["surface_ids"], module["path"]
        assert module["source_families"], module["path"]
        assert module["authority"] in authority_order, module["path"]
        assert module["source_route"] in authority_order, module["path"]
        assert "triangulation_status" in module, module["path"]


def test_duplicate_clusters_have_triangulation_and_valid_module_links() -> None:
    inventory = load_inventory()
    module_paths = {module["path"] for module in inventory["modules"]}
    assert inventory["duplicate_clusters"], "expected duplicate clusters"
    for cluster in inventory["duplicate_clusters"]:
        assert cluster["id"]
        assert cluster["canonical_module"] in module_paths, cluster["id"]
        assert "official" in cluster["source_systems"][0], cluster["id"]
        assert cluster["triangulation_method"], cluster["id"]
        assert cluster["reconciliation_status"], cluster["id"]
        for path in cluster["overlapping_modules"]:
            assert path in module_paths, path


def test_oracle_backed_duplicate_clusters_keep_official_sources_primary() -> None:
    inventory = load_inventory()
    oracle_ids = {"policyengine-nz", "openfisca-aotearoa", "nztaxmicrosim"}
    for cluster in inventory["duplicate_clusters"]:
        if oracle_ids.intersection(cluster["source_systems"]):
            assert "official" in cluster["source_systems"][0], cluster["id"]
            method = cluster["triangulation_method"].lower()
            assert "official" in method
            assert "prevail" in method or "canonical" in method


# ── Phase 2: Rule-level Extraction ────────────────────────────────────


def test_inventory_status_is_rule_level_complete() -> None:
    """Inventory must be updated to rule_level_complete after Phase 2 extraction."""
    inventory = load_inventory()
    assert inventory["module_inventory_status"] == "rule_level_complete", (
        "Run Phase 2 rule extraction before marking this test pass"
    )


def test_every_rulespec_module_records_rules() -> None:
    """Each module in the inventory must have a 'rules' list with extracted rule names."""
    inventory = load_inventory()
    for module in inventory["modules"]:
        path = module["path"]
        rules = module.get("rules")
        assert rules is not None, f"{path} missing 'rules' key"
        assert isinstance(rules, list), f"{path} 'rules' must be a list"
        yaml_rules = rulespec_rule_names(ROOT / path)
        assert len(rules) == len(yaml_rules), (
            f"{path}: inventory has {len(rules)} rules but YAML has {len(yaml_rules)}"
        )


def test_every_rule_name_is_represented_in_inventory() -> None:
    """Every rules[].name from every non-test YAML must appear in the inventory."""
    inventory = load_inventory()
    inventoried_rules: dict[str, list[str]] = {}

    for module in inventory["modules"]:
        path = module["path"]
        inventoried_rules[path] = [
            r["name"] for r in module.get("rules", []) if isinstance(r, dict)
        ]

    for path_str in sorted(non_test_rulespec_paths()):
        yaml_rules = rulespec_rule_names(ROOT / path_str)
        yaml_names = {r["name"] for r in yaml_rules}
        inv_names = set(inventoried_rules.get(path_str, []))
        missing = yaml_names - inv_names
        assert not missing, f"{path_str}: rule(s) {missing} not in inventory"


def test_stable_rule_identifiers_are_unique() -> None:
    """Every rule in the inventory must have a stable identifier that is unique repo-wide."""
    inventory = load_inventory()
    ids: list[str] = []
    for module in inventory["modules"]:
        for rule in module.get("rules", []):
            if isinstance(rule, dict) and rule.get("id"):
                ids.append(str(rule["id"]))
            elif isinstance(rule, dict) and rule.get("name"):
                ids.append(canonical_rule_id(module["path"], str(rule["name"])))
            else:
                ids.append(f"{module['path']}:no_name")
    assert len(ids) == len(set(ids)), (
        f"Duplicate rule identifiers found: "
        f"{[i for i in set(ids) if ids.count(i) > 1]}"
    )


def test_rule_identifiers_are_deterministic() -> None:
    """Stable identifiers must be accessible in the inventory via the 'id' field."""
    inventory = load_inventory()
    for module in inventory["modules"]:
        for rule in module.get("rules", []):
            if not isinstance(rule, dict):
                continue
            assert "id" in rule, (
                f"{module['path']}#{rule.get('name', '?')} missing 'id' field"
            )
            expected = canonical_rule_id(module["path"], str(rule.get("name", "")))
            assert rule["id"] == expected, (
                f"{module['path']}#{rule.get('name')}: "
                f"expected id '{expected}', got '{rule['id']}'"
            )


def test_module_with_empty_rules_has_empty_inventory_rules() -> None:
    """Modules with rules: [] (deferred) must still appear in inventory with empty rules list."""
    inventory = load_inventory()
    for module in inventory["modules"]:
        path = module["path"]
        yaml_rules = rulespec_rule_names(ROOT / path)
        if len(yaml_rules) == 0:
            inv_rules = module.get("rules", [])
            assert inv_rules == [], (
                f"{path}: YAML has 0 rules but inventory has {len(inv_rules)}"
            )


def test_rule_level_provenance_fields_present() -> None:
    """Each rule in the inventory should record provenance fields: source_family and kind."""
    inventory = load_inventory()
    for module in inventory["modules"]:
        for rule in module.get("rules", []):
            if not isinstance(rule, dict):
                continue
            assert "kind" in rule, (
                f"{module['path']}#{rule.get('name', '?')} missing 'kind'"
            )
            assert "source_family" in rule, (
                f"{module['path']}#{rule.get('name', '?')} missing 'source_family'"
            )
            assert isinstance(rule["source_family"], str), (
                f"{module['path']}#{rule.get('name', '?')} 'source_family' must be str"
            )
