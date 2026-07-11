"""Canonical RuleSpec-NZ filesystem discovery for repository tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ATOMIC_CONTENT_ROOTS = ("legislation", "policies", "regulations", "statutes")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class RuleSpecLayoutError(ValueError):
    """Canonical RuleSpec filesystem discovery failed closed."""


def atomic_rulespec_paths(repository_root: Path = REPOSITORY_ROOT) -> tuple[Path, ...]:
    """Return primary modules from only the four direct NZ atomic roots."""
    jurisdiction = repository_root / "nz"
    if jurisdiction.is_symlink():
        message = f"jurisdiction root must not be an alias: {jurisdiction}"
        raise RuleSpecLayoutError(message)

    paths: list[Path] = []
    for source_root in ATOMIC_CONTENT_ROOTS:
        content_root = jurisdiction / source_root
        if not content_root.exists() and not content_root.is_symlink():
            continue
        if content_root.is_symlink() or not content_root.is_dir():
            message = f"atomic root must be a regular directory: {content_root}"
            raise RuleSpecLayoutError(message)
        for path in sorted(content_root.rglob("*")):
            if path.is_symlink():
                message = f"atomic RuleSpec content must not be an alias: {path}"
                raise RuleSpecLayoutError(message)
            if not path.is_file():
                continue
            if path.suffix.lower() in {".yaml", ".yml"} and path.suffix != ".yaml":
                message = f"atomic RuleSpec must use exact .yaml: {path}"
                raise RuleSpecLayoutError(message)
            if path.suffix == ".yaml" and not path.name.endswith(".test.yaml"):
                paths.append(path)
    return tuple(paths)


def corpus_proof_paths(payload: dict[str, Any]) -> set[str]:
    """Return the singular module source and direct rule-proof corpus paths."""
    paths: set[str] = set()
    module = payload.get("module")
    if isinstance(module, dict):
        verification = module.get("source_verification")
        if isinstance(verification, dict):
            primary = verification.get("corpus_citation_path")
            if isinstance(primary, str) and primary:
                paths.add(primary)

    rules = payload.get("rules")
    if not isinstance(rules, list):
        return paths
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        metadata = rule.get("metadata")
        proof = metadata.get("proof") if isinstance(metadata, dict) else None
        atoms = proof.get("atoms") if isinstance(proof, dict) else None
        if not isinstance(atoms, list):
            continue
        for atom in atoms:
            source = atom.get("source") if isinstance(atom, dict) else None
            citation_path = (
                source.get("corpus_citation_path")
                if isinstance(source, dict)
                else None
            )
            if isinstance(citation_path, str) and citation_path:
                paths.add(citation_path)
    return paths
