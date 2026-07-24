from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import yaml

from scripts.rulespec_layout import atomic_rulespec_paths


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "data/corpus/canonical-provenance-migration-blockers.json"
ALLOWED_SOURCE_VERIFICATION_KEYS = {"corpus_citation_path", "source_sha256"}


def _modules() -> dict[str, dict[str, Any]]:
    modules: dict[str, dict[str, Any]] = {}
    for path in atomic_rulespec_paths(ROOT):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(payload, dict)
        modules[path.relative_to(ROOT).as_posix()] = cast("dict[str, Any]", payload)
    return modules


def _proof_atoms(rule: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = rule.get("metadata")
    proof = metadata.get("proof") if isinstance(metadata, dict) else None
    atoms = proof.get("atoms") if isinstance(proof, dict) else None
    assert isinstance(atoms, list)
    assert atoms
    assert all(isinstance(atom, dict) for atom in atoms)
    return cast("list[dict[str, Any]]", atoms)


def test_atomic_modules_use_only_singular_fail_closed_provenance() -> None:
    modules = _modules()
    proof_atom_count = 0

    assert len(modules) == 40
    for relative, payload in modules.items():
        module = payload.get("module")
        assert isinstance(module, dict), relative
        assert module.get("proof_validation") == {"required": True}, relative

        source_verification = module.get("source_verification")
        assert isinstance(source_verification, dict), relative
        assert set(source_verification) <= ALLOWED_SOURCE_VERIFICATION_KEYS, relative
        assert isinstance(source_verification.get("corpus_citation_path"), str), (
            relative
        )

        rules = payload.get("rules")
        assert isinstance(rules, list), relative
        for rule in rules:
            assert isinstance(rule, dict), relative
            atoms = _proof_atoms(cast("dict[str, Any]", rule))
            proof_atom_count += len(atoms)
            for atom in atoms:
                assert isinstance(atom.get("path"), str), (relative, rule.get("name"))
                assert isinstance(atom.get("kind"), str), (relative, rule.get("name"))
                source = atom.get("source")
                assert isinstance(source, dict), (relative, rule.get("name"))
                assert (
                    {"corpus_citation_path"}
                    <= set(source)
                    <= {
                        "corpus_citation_path",
                        "excerpt",
                    }
                ), (relative, rule.get("name"))
                assert isinstance(source["corpus_citation_path"], str)
                if "excerpt" in source:
                    assert isinstance(source["excerpt"], str)
                    assert source["excerpt"]

    assert proof_atom_count == 1189
    assert list((ROOT / ".axiom/encoding-manifests").rglob("*.json")) == []


def test_provenance_blocker_ledger_matches_direct_rule_proofs() -> None:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    modules = _modules()

    assert ledger["schema_version"] == (
        "axiom-rulespec/provenance-migration-blockers/v1"
    )
    assert ledger["release_cut_plan"] == "nz-rulespec-2026-07-20"
    assert ledger["publication_state"] == "merged_published_activated"
    assert ledger["atomic_module_count"] == len(modules) == 40
    assert ledger["proof_atom_count"] == 1189
    assert ledger["resolved_proof_atom_count"] == 1080
    assert ledger["blocked_proof_atom_count"] == 109

    blockers = ledger["blockers"]
    assert isinstance(blockers, list)
    assert len(blockers) == 19
    blocker_paths = [blocker["citation_path"] for blocker in blockers]
    assert len(blocker_paths) == len(set(blocker_paths))

    blocked_atoms_by_path: dict[str, list[tuple[str, str]]] = {
        path: [] for path in blocker_paths
    }
    for module_path, payload in modules.items():
        for rule in payload["rules"]:
            assert isinstance(rule, dict)
            for atom in _proof_atoms(cast("dict[str, Any]", rule)):
                citation_path = atom["source"]["corpus_citation_path"]
                if citation_path in blocked_atoms_by_path:
                    blocked_atoms_by_path[citation_path].append(
                        (module_path, rule["name"]),
                    )

    affected_rule_ids: set[tuple[str, str]] = set()
    blocked_proof_atom_count = 0

    for blocker in blockers:
        assert isinstance(blocker, dict)
        citation_path = blocker["citation_path"]
        affected_rules = blocker["affected_rules"]
        assert isinstance(citation_path, str)
        assert isinstance(affected_rules, list)
        assert blocker["affected_rule_count"] == len(affected_rules)
        assert blocker["required_official_source_document"]
        assert blocker["official_source_urls"]
        assert blocker["required_release_action"]

        actual_atoms = blocked_atoms_by_path[citation_path]
        actual_rule_ids = set(actual_atoms)
        actual_module_paths = {module_path for module_path, _ in actual_atoms}
        expected_rule_ids = {
            (affected["module"], affected["rule"]) for affected in affected_rules
        }
        assert blocker["blocked_proof_atom_count"] == len(actual_atoms)
        assert blocker["affected_rule_count"] == len(actual_rule_ids)
        assert blocker["affected_module_count"] == len(actual_module_paths)
        assert expected_rule_ids == actual_rule_ids
        blocked_proof_atom_count += len(actual_atoms)

        for affected in affected_rules:
            assert isinstance(affected, dict)
            module_path = affected["module"]
            rule_name = affected["rule"]
            payload = modules[module_path]
            rule = next(
                item
                for item in payload["rules"]
                if isinstance(item, dict) and item.get("name") == rule_name
            )
            proof_paths = {
                atom["source"]["corpus_citation_path"]
                for atom in _proof_atoms(cast("dict[str, Any]", rule))
            }
            assert citation_path in proof_paths, (module_path, rule_name, citation_path)
            affected_rule_ids.add((module_path, rule_name))

    assert len(affected_rule_ids) == 88
    assert blocked_proof_atom_count == ledger["blocked_proof_atom_count"] == 109
