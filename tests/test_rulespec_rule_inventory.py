from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"


def load_inventory() -> dict:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig"))


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
    assert (
        inventory["module_inventory_status"]
        == "module_level_complete_rule_level_pending"
    )
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
