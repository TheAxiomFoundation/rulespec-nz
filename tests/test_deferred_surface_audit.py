"""Phase 1-2: Deferred Surface Audit and Extraction Units for nztaxmicrosim follow-on reconciliation.

Phase 1 tests verify that the source map correctly documents all deferred surfaces
and that each deferred surface has complete official-source requirements.
Phase 2 tests verify extraction units are properly defined for all deferred surfaces.
"""

from __future__ import annotations
# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_MAP_PATH = ROOT / "data" / "coverage" / "nztaxmicrosim-source-map.json"
RECONCILIATION_PATH = ROOT / "data" / "coverage" / "nztaxmicrosim-reconciliation.json"
INVENTORY_PATH = ROOT / "data" / "oracles" / "nztaxmicrosim-rule-inventory.json"


def load_json(path: Path) -> dict:
    return dict(json.loads(path.read_text(encoding="utf-8-sig")))


def deferred_surface_ids_from_reconciliation() -> set[str]:
    reconciliation = load_json(RECONCILIATION_PATH)
    return {
        surface["id"]
        for surface in reconciliation["surfaces"]
        if surface["closeout_status"].startswith("deferred")
    }


def deferred_surface_ids_from_source_map() -> set[str]:
    source_map = load_json(SOURCE_MAP_PATH)
    return {
        surface["id"]
        for surface in source_map["surfaces"]
        if surface["implementation_status"].startswith("missing")
    }


@pytest.mark.unit
def test_deferred_surfaces_match_between_reconciliation_and_source_map() -> None:
    """Every deferred surface in reconciliation must also be present and marked missing in the source map."""
    rec_deferred = deferred_surface_ids_from_reconciliation()
    map_deferred = deferred_surface_ids_from_source_map()
    assert rec_deferred == map_deferred, (
        f"Reconciliation deferred {rec_deferred} != source-map missing {map_deferred}"
    )


@pytest.mark.unit
def test_each_deferred_surface_has_planned_rulespec_destinations() -> None:
    """Every deferred/missing surface in the source map must list planned rulespec paths and official sources."""
    source_map = load_json(SOURCE_MAP_PATH)
    for surface in source_map["surfaces"]:
        if not surface["implementation_status"].startswith("missing"):
            continue
        assert surface.get("planned_rulespec_paths"), (
            f"{surface['id']} missing planned_rulespec_paths"
        )
        assert surface.get("official_sources"), (
            f"{surface['id']} missing official_sources"
        )
        for path in surface["planned_rulespec_paths"]:
            assert path.startswith("nz/"), (
                f"{surface['id']} path not in nz/ root: {path}"
            )


@pytest.mark.unit
def test_deferred_surfaces_have_corresponding_oracle_inventory_entries() -> None:
    """Each deferred surface must appear in the nztaxmicrosim rule inventory with status missing and reference planned destinations."""
    inventory = load_json(INVENTORY_PATH)
    inventory_surfaces = {s["id"]: s for s in inventory["rule_surfaces"]}
    source_map = load_json(SOURCE_MAP_PATH)

    for surface in source_map["surfaces"]:
        if not surface["implementation_status"].startswith("missing"):
            continue
        sid = surface["id"]
        assert sid in inventory_surfaces, (
            f"{sid} missing from nztaxmicrosim rule inventory"
        )
        inv_surface = inventory_surfaces[sid]
        assert inv_surface["status"] == "missing", (
            f"{sid} in inventory status is {inv_surface['status']}, expected 'missing'"
        )
        planned_dest = inv_surface.get("planned_destinations", [])
        assert set(planned_dest) == set(surface["planned_rulespec_paths"]), (
            f"{sid} planned destinations mismatch between inventory and source-map"
        )


@pytest.mark.unit
def test_deferred_surfaces_identify_oracle_limitations() -> None:
    """Oracle limitations must be documented for surfaces whose oracle logic is simplified and cannot be encoded canonically."""
    inventory = load_json(INVENTORY_PATH)
    inventory_surfaces = {s["id"]: s for s in inventory["rule_surfaces"]}
    source_map = load_json(SOURCE_MAP_PATH)

    for surface in source_map["surfaces"]:
        if not surface["implementation_status"].startswith("missing"):
            continue
        sid = surface["id"]
        inv_surface = inventory_surfaces[sid]
        limitations = inv_surface.get("oracle_limitations", [])
        blockers = surface.get("blockers", [])

        # Surfaces with blockers (simplified oracle) must have limitations documented
        if blockers:
            assert limitations, (
                f"{sid} has blockers but no oracle_limitations documented"
            )
            assert any("simplified" in str(b).lower() for b in blockers), (
                f"{sid} blockers should reference simplified oracle logic"
            )


# --- Task 2: Extraction Unit Manifest Tests ---

EXTRACTION_MANIFEST_PATH = (
    ROOT / "data" / "oracles" / "nztaxmicrosim-extraction-units.json"
)


@pytest.mark.unit
def test_extraction_manifest_exists() -> None:
    """An extraction units manifest must exist at the expected path."""
    assert EXTRACTION_MANIFEST_PATH.exists(), (
        f"Extraction manifest not found at {EXTRACTION_MANIFEST_PATH}"
    )


@pytest.mark.unit
def test_extraction_manifest_covers_all_deferred_surfaces() -> None:
    """The extraction manifest must have an entry for every deferred surface."""
    manifest = load_json(EXTRACTION_MANIFEST_PATH)
    deferred = deferred_surface_ids_from_reconciliation()
    manifest_surfaces = {unit["surface_id"] for unit in manifest["extraction_units"]}
    assert deferred == manifest_surfaces, (
        f"Manifest surfaces {manifest_surfaces} != deferred {deferred}"
    )


@pytest.mark.unit
def test_each_extraction_unit_has_target_path_and_source() -> None:
    """Each extraction unit must specify its rulespec target path, official source, and kind. Target paths must be within nz/ root."""
    manifest = load_json(EXTRACTION_MANIFEST_PATH)
    for unit in manifest["extraction_units"]:
        assert unit.get("target_path"), f"{unit['surface_id']} missing target_path"
        assert unit.get("official_source"), (
            f"{unit['surface_id']} missing official_source"
        )
        assert unit.get("kind"), f"{unit['surface_id']} missing kind"
        tp = unit["target_path"]
        assert tp.startswith("nz/"), f"{unit['surface_id']} path not in nz/: {tp}"


@pytest.mark.unit
def test_extraction_units_are_not_simplified_oracle_promotions() -> None:
    """Every extraction unit must confirm no simplified oracle logic is promoted as canonical."""
    manifest = load_json(EXTRACTION_MANIFEST_PATH)
    for unit in manifest["extraction_units"]:
        note = unit.get("oracle_constraint", "")
        assert note, f"{unit['surface_id']} missing oracle_constraint note"
        assert "simplified" not in unit.get("kind", ""), (
            f"{unit['surface_id']} kind should not reference simplified"
        )
