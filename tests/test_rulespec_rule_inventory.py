from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any, cast

import yaml


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"


@functools.cache
def load_inventory() -> dict[str, Any]:
    return cast(
        dict[str, Any], json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))
    )


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
        f"Duplicate rule identifiers found: {[i for i in set(ids) if ids.count(i) > 1]}"
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


# ── Phase 3: Reconciliation Workflow ─────────────────────────────────


def load_reconciliation(path: Path) -> dict[str, Any] | None:
    """Load a reconciliation file if it exists."""
    if not path.exists():
        return None
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def test_duplicate_clusters_link_to_reconciliation_surfaces() -> None:
    """Each duplicate cluster must link its oracle reconciliation surfaces."""
    inventory = load_inventory()
    recon_paths = {
        "policyengine-nz": Path(
            ROOT / "data/coverage/policyengine-nz-reconciliation.json"
        ),
        "openfisca-aotearoa": Path(
            ROOT / "data/coverage/openfisca-aotearoa-reconciliation.json"
        ),
        "nztaxmicrosim": Path(ROOT / "data/coverage/nztaxmicrosim-reconciliation.json"),
    }
    oracle_ids = {"policyengine-nz", "openfisca-aotearoa", "nztaxmicrosim"}
    for cluster in inventory["duplicate_clusters"]:
        assert "reconciliation_surface_links" in cluster, (
            f"{cluster['id']} missing 'reconciliation_surface_links'"
        )
        links = cluster["reconciliation_surface_links"]
        assert isinstance(links, list), (
            f"{cluster['id']} reconciliation_surface_links must be list"
        )
        for link in links:
            assert "oracle_id" in link, f"{cluster['id']} link missing oracle_id"
            assert "surface_id" in link, f"{cluster['id']} link missing surface_id"
            assert link["oracle_id"] in oracle_ids, (
                f"{cluster['id']}: unknown oracle_id {link['oracle_id']}"
            )
            recon = load_reconciliation(recon_paths[link["oracle_id"]])
            if recon is not None:
                surface_ids = {s["id"] for s in recon.get("surfaces", [])}
                assert link["surface_id"] in surface_ids, (
                    f"{cluster['id']}: surface_id '{link['surface_id']}' "
                    f"not found in {link['oracle_id']} reconciliation"
                )


def test_duplicate_clusters_declare_conflicts() -> None:
    """Each duplicate cluster must declare known conflicts."""
    inventory = load_inventory()
    for cluster in inventory["duplicate_clusters"]:
        assert "conflicts" in cluster, f"{cluster['id']} missing 'conflicts' key"
        assert isinstance(cluster["conflicts"], list), (
            f"{cluster['id']} conflicts must be a list"
        )
        for conflict in cluster["conflicts"]:
            assert "type" in conflict, f"{cluster['id']} conflict missing 'type'"
            assert conflict["type"] in (
                "value_mismatch",
                "scope_mismatch",
                "stale_oracle",
            ), f"{cluster['id']} conflict type '{conflict['type']}' invalid"
            assert "status" in conflict, f"{cluster['id']} conflict missing 'status'"
            assert conflict["status"] in (
                "unresolved",
                "resolved_official_source",
            ), f"{cluster['id']} conflict status '{conflict['status']}' invalid"


def test_resolved_conflicts_record_official_source_decision() -> None:
    """Resolved conflicts must record an official-source decision."""
    inventory = load_inventory()
    for cluster in inventory["duplicate_clusters"]:
        for conflict in cluster.get("conflicts", []):
            if conflict.get("status") == "resolved_official_source":
                assert "official_source_decision" in conflict, (
                    f"{cluster['id']} resolved conflict missing "
                    "'official_source_decision'"
                )
                decision = conflict["official_source_decision"]
                assert isinstance(decision, str), (
                    f"{cluster['id']} official_source_decision must be a string"
                )
                assert len(decision) > 10, (
                    f"{cluster['id']} official_source_decision too short"
                )


def test_all_oracle_reconciliation_files_exist() -> None:
    """Reconciliation files for all three oracles must exist on disk."""
    paths = [
        ROOT / "data/coverage/policyengine-nz-reconciliation.json",
        ROOT / "data/coverage/openfisca-aotearoa-reconciliation.json",
        ROOT / "data/coverage/nztaxmicrosim-reconciliation.json",
    ]
    for p in paths:
        assert p.exists(), f"Missing reconciliation file: {p}"


# ── Phase 4: Reporting ───────────────────────────────────────────────


SCORECARD_PATH = ROOT / "data" / "coverage" / "rulespec-scorecard.json"


def load_scorecard() -> dict[str, Any] | None:
    if SCORECARD_PATH.exists():
        return cast(
            dict[str, Any], json.loads(SCORECARD_PATH.read_text(encoding="utf-8"))
        )
    return None


def test_scorecard_exists() -> None:
    """A compact completion scorecard must be generated from the inventory."""
    scorecard = load_scorecard()
    assert scorecard is not None, (
        f"Scorecard not found at {SCORECARD_PATH}. Run scripts/phase4_scorecard.py"
    )


def test_scorecard_has_summary_fields() -> None:
    """Scorecard must contain summary metrics."""
    scorecard = load_scorecard()
    assert scorecard is not None
    required = {
        "generated_at",
        "jurisdiction",
        "total_modules",
        "modules_with_rules",
        "modules_deferred",
        "total_rules",
        "total_duplicate_clusters",
        "total_conflicts",
        "resolved_conflicts",
        "unresolved_conflicts",
    }
    missing = required - set(scorecard)
    assert not missing, f"Scorecard missing fields: {missing}"


def test_scorecard_counts_agree_with_inventory() -> None:
    """Scorecard module/rule counts must match the inventory."""
    inventory = load_inventory()
    scorecard = load_scorecard()
    assert scorecard is not None

    total_modules = len(inventory["modules"])
    modules_with_rules = sum(1 for m in inventory["modules"] if m.get("rules"))
    modules_deferred = sum(
        1
        for m in inventory["modules"]
        if not m.get("rules") or len(m.get("rules", [])) == 0
    )
    total_rules = sum(len(m.get("rules", [])) for m in inventory["modules"])

    assert scorecard["total_modules"] == total_modules, (
        f"total_modules mismatch: {scorecard['total_modules']} vs {total_modules}"
    )
    assert scorecard["modules_with_rules"] == modules_with_rules
    assert scorecard["modules_deferred"] == modules_deferred
    assert scorecard["total_rules"] == total_rules


def test_scorecard_duplicate_cluster_counts_match() -> None:
    """Scorecard conflict counts must match inventory clusters."""
    inventory = load_inventory()
    scorecard = load_scorecard()
    assert scorecard is not None

    total_clusters = len(inventory["duplicate_clusters"])
    total_conflicts = sum(
        len(c.get("conflicts", [])) for c in inventory["duplicate_clusters"]
    )
    resolved = sum(
        1
        for c in inventory["duplicate_clusters"]
        for cf in c.get("conflicts", [])
        if cf.get("status") == "resolved_official_source"
    )
    unresolved = sum(
        1
        for c in inventory["duplicate_clusters"]
        for cf in c.get("conflicts", [])
        if cf.get("status") == "unresolved"
    )

    assert scorecard["total_duplicate_clusters"] == total_clusters
    assert scorecard["total_conflicts"] == total_conflicts
    assert scorecard["resolved_conflicts"] == resolved
    assert scorecard["unresolved_conflicts"] == unresolved


def test_scorecard_has_status_view() -> None:
    """Scorecard must include a status view for each module."""
    scorecard = load_scorecard()
    assert scorecard is not None
    assert "status_view" in scorecard, "Scorecard missing 'status_view'"
    view = scorecard["status_view"]
    assert isinstance(view, dict), "status_view must be a dict"

    required_categories = {"encoded", "deferred", "blocked"}
    present = set(view)
    missing = required_categories - present
    # extracted-not-encoded is optional
    assert not missing, f"status_view missing categories: {missing}"

    for category, modules in view.items():
        assert isinstance(modules, list), f"status_view.{category} must be a list"
        for mod in modules:
            if isinstance(mod, str):
                assert (ROOT / mod).exists(), f"status_view.{category}: {mod} not found"
            elif isinstance(mod, dict):
                assert "path" in mod, f"status_view.{category} item missing 'path'"
                assert (ROOT / mod["path"]).exists(), (
                    f"status_view.{category}: {mod['path']} not found"
                )
