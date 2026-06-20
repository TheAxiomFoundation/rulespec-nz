from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OPENFISCA_ORACLE_ID = "openfisca-aotearoa"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _find_openfisca_oracle(oracle_index: dict[str, Any]) -> dict[str, Any]:
    for oracle in oracle_index.get("oracles", []):
        if oracle.get("id") == OPENFISCA_ORACLE_ID:
            return oracle
    raise ValueError(f"Missing oracle index entry: {OPENFISCA_ORACLE_ID}")


def _openfisca_tracks(source_map: dict[str, Any]) -> list[dict[str, Any]]:
    tracks: list[dict[str, Any]] = []
    for track in source_map.get("tracks", []):
        for oracle_surface in track.get("oracle_surfaces", []):
            if oracle_surface.get("oracle_id") != OPENFISCA_ORACLE_ID:
                continue
            files = [str(file_ref) for file_ref in oracle_surface.get("files", [])]
            tracks.append(
                {
                    "track_id": str(track["track_id"]),
                    "role": str(oracle_surface.get("role", "comparison oracle")),
                    "files": files,
                    "canonical_law": False,
                    "authority": "comparison_oracle",
                }
            )
    return tracks


def build_openfisca_reference_manifest(root: Path) -> dict[str, Any]:
    """Build a guarded OpenFisca comparison-reference manifest.

    OpenFisca references are useful for parity checks and fixture extraction,
    but official NZ source law remains canonical. The returned manifest keeps
    the pinned oracle commit and marks every record as non-authoritative.
    """
    oracle_index = _load_json(root / "data" / "oracles" / "oracle-index.json")
    source_map = _load_json(root / "data" / "coverage" / "tax-benefit-source-map.json")
    oracle = _find_openfisca_oracle(oracle_index)
    tracks = _openfisca_tracks(source_map)

    return {
        "adapter": "openfisca-aotearoa-reference-intake",
        "canonical_law": False,
        "authority": "comparison_oracle",
        "oracle": {
            "id": oracle["id"],
            "name": oracle["name"],
            "url": oracle["url"],
            "commit": oracle["commit"],
        },
        "tracks": tracks,
    }