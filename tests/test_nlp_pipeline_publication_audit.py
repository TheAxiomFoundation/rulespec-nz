"""Tests for Track 17: NLP Pipeline and Publication Audit.

Covers Phases 1-4: local manifest audit, live publication verification,
source-precedence decisions, and inventory integration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[1]
AUDIT_MANIFEST_PATH = (
    ROOT / "data" / "corpus" / "ingestion" / "nlp-pipeline-publication-audit.json"
)
INVENTORY_PATH = ROOT / "data" / "coverage" / "rulespec-rule-inventory.json"
ORACLE_INDEX_PATH = ROOT / "data" / "oracles" / "oracle-index.json"
PARQUET_LAYERS_PATH = (
    ROOT / "data" / "corpus" / "ingestion" / "local-parquet-layers.json"
)
NZ_LEGISLATION_PATH = ROOT / "data" / "corpus" / "ingestion" / "nz-legislation.json"

NLP_SOURCE_IDS = {"nlp-policy-nz", "corpus-legislation-nz", "nz-legislation"}
VERIFIED_SOURCE_CLASSIFICATIONS = {
    "authoritative_source",
    "normalized_official_source_mirror",
    "supporting_source_tool",
    "stale_unverified",
}
PUBLICATION_PLATFORMS = {"github", "huggingface", "zenodo"}


def load_audit_manifest() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(AUDIT_MANIFEST_PATH.read_text(encoding="utf-8-sig")),
    )


def load_inventory() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(INVENTORY_PATH.read_text(encoding="utf-8-sig")),
    )


def load_oracle_index() -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(ORACLE_INDEX_PATH.read_text(encoding="utf-8-sig")),
    )


# Phase 1: Local Manifest Audit


def test_audit_manifest_exists() -> None:
    assert AUDIT_MANIFEST_PATH.exists(), (
        f"Audit manifest not found at {AUDIT_MANIFEST_PATH}"
    )


def test_audit_manifest_has_required_top_level_fields() -> None:
    manifest = load_audit_manifest()
    required = {
        "generated_at",
        "track_id",
        "jurisdiction",
        "purpose",
        "pipeline_sources",
        "local_verified_facts",
        "publication_state_claims",
        "source_precedence",
    }
    missing = required - set(manifest)
    assert not missing, f"Manifest missing fields: {missing}"


def test_audit_manifest_records_all_nlp_pipeline_sources() -> None:
    manifest = load_audit_manifest()
    sources = manifest.get("pipeline_sources", {})
    assert isinstance(sources, dict), "pipeline_sources must be a dict"
    assert set(sources) == NLP_SOURCE_IDS, (
        f"Expected sources {NLP_SOURCE_IDS}, got {set(sources)}"
    )


def test_every_pipeline_source_has_required_fields() -> None:
    manifest = load_audit_manifest()
    required_fields = {"id", "oracle_entry", "local_facts", "publication_state"}
    for source_id, source_data in manifest.get("pipeline_sources", {}).items():
        assert isinstance(source_data, dict), f"{source_id} must be a dict"
        missing = required_fields - set(source_data)
        assert not missing, f"{source_id} missing fields: {missing}"
        assert source_data.get("id") == source_id, f"{source_id}: id mismatch"


def test_oracle_entry_references_existing_oracle() -> None:
    manifest = load_audit_manifest()
    oracle_index = load_oracle_index()
    oracle_ids = {o["id"] for o in oracle_index.get("oracles", [])}
    for source_id, source_data in manifest.get("pipeline_sources", {}).items():
        oracle_entry = source_data.get("oracle_entry", {})
        oracle_id = oracle_entry.get("oracle_id", source_id)
        assert oracle_id in oracle_ids, (
            f"{source_id}: oracle_id '{oracle_id}' not in oracle-index"
        )


def test_local_facts_separate_from_publication_claims() -> None:
    manifest = load_audit_manifest()
    assert "local_verified_facts" in manifest
    assert "publication_state_claims" in manifest
    assert isinstance(manifest["local_verified_facts"], dict)
    assert isinstance(manifest["publication_state_claims"], dict)


def test_local_verified_facts_have_expected_keys() -> None:
    manifest = load_audit_manifest()
    local = manifest.get("local_verified_facts", {})
    expected = {
        "parquet_layer_status",
        "nz_legislation_extraction",
        "oracle_pinned_commits",
    }
    missing = expected - set(local)
    assert not missing, f"local_verified_facts missing keys: {missing}"


def test_publication_state_claims_cover_all_sources() -> None:
    manifest = load_audit_manifest()
    claims = manifest.get("publication_state_claims", {})
    claimed_ids = set(claims.keys())
    assert NLP_SOURCE_IDS.issubset(claimed_ids), (
        f"Missing claims for: {NLP_SOURCE_IDS - claimed_ids}"
    )
    for source_id in NLP_SOURCE_IDS:
        source_claims = claims.get(source_id, {})
        platforms = set(source_claims.keys())
        assert PUBLICATION_PLATFORMS.issubset(platforms), (
            f"{source_id}: missing platforms {PUBLICATION_PLATFORMS - platforms}"
        )


def test_every_source_classified_in_manifest() -> None:
    manifest = load_audit_manifest()
    for source_id, source_data in manifest.get("pipeline_sources", {}).items():
        classification = source_data.get("classification")
        assert classification is not None, f"{source_id} missing classification"
        assert classification in VERIFIED_SOURCE_CLASSIFICATIONS, (
            f"{source_id}: invalid classification '{classification}'"
        )


# Phase 2: Live Publication Verification


def test_publication_state_claims_include_github_heads() -> None:
    manifest = load_audit_manifest()
    claims = manifest.get("publication_state_claims", {})
    for source_id in NLP_SOURCE_IDS:
        source_claims = claims.get(source_id, {})
        gh = source_claims.get("github", {})
        assert "head_sha" in gh, f"{source_id} github missing head_sha"
        assert "head_url" in gh, f"{source_id} github missing head_url"
        assert isinstance(gh["head_sha"], str), f"{source_id} head_sha not str"
        assert len(gh["head_sha"]) >= 7, f"{source_id} head_sha too short"


def test_publication_state_claims_include_huggingface() -> None:
    manifest = load_audit_manifest()
    claims = manifest.get("publication_state_claims", {})
    for source_id in NLP_SOURCE_IDS:
        source_claims = claims.get(source_id, {})
        hf = source_claims.get("huggingface", {})
        assert isinstance(hf, dict), f"{source_id} huggingface must be dict"
        has_id = any(
            k in hf for k in ("repository", "dataset", "space", "state", "notes")
        )
        assert has_id, f"{source_id} huggingface missing identifier"


def test_publication_state_claims_include_zenodo() -> None:
    manifest = load_audit_manifest()
    claims = manifest.get("publication_state_claims", {})
    for source_id in NLP_SOURCE_IDS:
        source_claims = claims.get(source_id, {})
        zenodo = source_claims.get("zenodo", {})
        assert isinstance(zenodo, dict), f"{source_id} zenodo must be dict"
        assert any(k in zenodo for k in ("doi", "version", "state", "notes")), (
            f"{source_id} zenodo missing identifier"
        )


def test_publication_state_claims_reflect_local_availability() -> None:
    manifest = load_audit_manifest()
    for source_id, source_data in manifest.get("pipeline_sources", {}).items():
        pub_state = source_data.get("publication_state", {})
        local_available = pub_state.get("local_extract_available")
        assert local_available is not None, (
            f"{source_id} missing local_extract_available"
        )
        assert isinstance(local_available, bool), f"{source_id} must be bool"


# Phase 3: Source-precedence Decision


def test_manifest_has_source_precedence_section() -> None:
    manifest = load_audit_manifest()
    precedence = manifest.get("source_precedence", {})
    assert "tiers" in precedence, "source_precedence missing 'tiers'"
    tiers = precedence["tiers"]
    assert isinstance(tiers, list), "tiers must be a list"
    assert len(tiers) >= 3, "Need at least 3 precedence tiers"


def test_source_precedence_tiers_are_specific() -> None:
    manifest = load_audit_manifest()
    tiers = manifest.get("source_precedence", {}).get("tiers", [])
    for i, tier in enumerate(tiers):
        assert "name" in tier, f"tier {i} missing 'name'"
        assert "sources" in tier, f"tier {i} missing 'sources'"
        assert "condition" in tier, f"tier {i} missing 'condition'"
        assert isinstance(tier["sources"], list), f"tier {i} sources not list"
        assert len(tier["sources"]) >= 1, f"tier {i} has empty sources"


def test_nlp_preferred_over_cli_when_verified() -> None:
    manifest = load_audit_manifest()
    precedence = manifest.get("source_precedence", {})
    decision = precedence.get("nlp_vs_cli_decision", "")
    assert "verified" in decision.lower(), "must reference verified state"
    assert "prefer" in decision.lower() or "preferred" in decision.lower(), (
        "must indicate preference"
    )


def test_fallback_route_defined() -> None:
    manifest = load_audit_manifest()
    precedence = manifest.get("source_precedence", {})
    fallback = precedence.get("fallback", "")
    assert fallback, "source_precedence missing 'fallback'"
    assert (
        "pco" in fallback.lower()
        or "cli" in fallback.lower()
        or "xml" in fallback.lower()
    ), "fallback must reference PCO bulk XML or NZ legislation CLI"


# Phase 4: Inventory Integration


def test_inventory_authority_order_includes_nlp_entries() -> None:
    inventory = load_inventory()
    assert "nlp_official_source_extract" in inventory.get("authority_order", []), (
        "authority_order missing nlp_official_source_extract"
    )
    order = inventory["authority_order"]
    nlp_idx = order.index("nlp_official_source_extract")
    pco_idx = order.index("pco_bulk_xml_extract")
    cli_idx = order.index("nz_legislation_cli_fallback")
    assert nlp_idx < pco_idx, "nlp must rank above pco"
    assert nlp_idx < cli_idx, "nlp must rank above cli"


def test_inventory_source_route_policy_references_nlp() -> None:
    inventory = load_inventory()
    policy = inventory.get("source_route_policy", "").lower()
    assert "nlp" in policy or "corpus" in policy, "must reference NLP or corpus"
    assert "verified" in policy, "must reference verified state"


def test_inventory_nlp_route_available() -> None:
    inventory = load_inventory()
    assert "nlp_official_source_extract" in inventory.get("authority_order", []), (
        "nlp_official_source_extract must be in authority_order"
    )


def test_inventory_duplicate_clusters_keep_official_before_nlp() -> None:
    inventory = load_inventory()
    for cluster in inventory.get("duplicate_clusters", []):
        source_systems = cluster.get("source_systems", [])
        nlp_systems = [s for s in source_systems if "nlp" in s.lower()]
        official_systems = [s for s in source_systems if "official" in s.lower()]
        for nlp_s in nlp_systems:
            nlp_idx = source_systems.index(nlp_s)
            for off_s in official_systems:
                off_idx = source_systems.index(off_s)
                assert off_idx < nlp_idx, f"{cluster['id']}: official must precede NLP"


def test_audit_manifest_links_to_inventory() -> None:
    manifest = load_audit_manifest()
    integration = manifest.get("inventory_integration", {})
    assert isinstance(integration, dict), "inventory_integration must be dict"
    assert any(
        k in integration for k in ("modules_with_nlp_route", "notes", "status")
    ), "inventory_integration missing key fields"


# Cross-cutting: Consistency checks


def test_oracle_index_has_nlp_related_sources() -> None:
    oracle_index = load_oracle_index()
    oracle_ids = {o["id"] for o in oracle_index.get("oracles", [])}
    # nlp-policy-nz and nz-legislation are oracle entries; corpus-legislation-nz is corpus-only
    oracle_nlp_ids = {"nlp-policy-nz", "nz-legislation"}
    for sid in oracle_nlp_ids:
        assert sid in oracle_ids, f"NLP source '{sid}' missing from oracle-index"


def test_local_parquet_layers_references_nlp_sources() -> None:
    layers = cast(
        dict[str, Any],
        json.loads(
            PARQUET_LAYERS_PATH.read_text(encoding="utf-8-sig"),
        ),
    )
    source_ids = {s["id"] for s in layers.get("sources", [])}
    assert "corpus-legislation-nz" in source_ids, "missing corpus-legislation-nz"


def test_nz_legislation_ingestion_file_exists() -> None:
    assert NZ_LEGISLATION_PATH.exists(), (
        f"nz-legislation.json not found at {NZ_LEGISLATION_PATH}"
    )


def test_inventory_modules_with_nlp_route_have_provenance() -> None:
    inventory = load_inventory()
    for module in inventory.get("modules", []):
        if module.get("source_route") == "nlp_official_source_extract":
            assert "nlp_extract_provenance" in module, (
                f"{module['path']} missing nlp_extract_provenance"
            )
            prov = module["nlp_extract_provenance"]
            assert "citation_path" in prov, "missing citation_path"
            assert "extract_source" in prov, "missing extract_source"


@pytest.mark.skip(reason="Phase 2 live check; requires GitHub API access")
def test_live_github_heads_match_claims() -> None:
    """Live GitHub heads should match publication_state_claims (requires API)."""
