from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict, cast


OPENFISCA_ORACLE_ID = "openfisca-aotearoa"


JsonObject = dict[str, object]


class OracleManifest(TypedDict):
    id: str
    name: str
    url: str
    commit: str


class OpenFiscaTrackManifest(TypedDict):
    track_id: str
    role: str
    files: list[str]
    canonical_law: bool
    authority: str


class OpenFiscaReferenceManifest(TypedDict):
    adapter: str
    canonical_law: bool
    authority: str
    oracle: OracleManifest
    tracks: list[OpenFiscaTrackManifest]


def _load_json_object(path: Path) -> JsonObject:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return cast(JsonObject, loaded)


def _object_list(value: object, label: str) -> list[JsonObject]:
    if not isinstance(value, list):
        raise ValueError(f"Expected list for {label}")
    objects: list[JsonObject] = []
    for index, item in enumerate(cast(list[object], value)):
        if not isinstance(item, dict):
            raise ValueError(f"Expected object for {label}[{index}]")
        objects.append(cast(JsonObject, item))
    return objects


def _string_value(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Expected string for {label}")
    return value


def _string_list(value: object, label: str) -> list[str]:
    values: list[str] = []
    for index, item in enumerate(_object_or_list_items(value, label)):
        values.append(_string_value(item, f"{label}[{index}]"))
    return values


def _object_or_list_items(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"Expected list for {label}")
    return cast(list[object], value)


def _find_openfisca_oracle(oracle_index: JsonObject) -> OracleManifest:
    for oracle in _object_list(oracle_index.get("oracles", []), "oracles"):
        if oracle.get("id") == OPENFISCA_ORACLE_ID:
            return {
                "id": _string_value(oracle.get("id"), "oracle.id"),
                "name": _string_value(oracle.get("name"), "oracle.name"),
                "url": _string_value(oracle.get("url"), "oracle.url"),
                "commit": _string_value(oracle.get("commit"), "oracle.commit"),
            }
    raise ValueError(f"Missing oracle index entry: {OPENFISCA_ORACLE_ID}")


def _openfisca_tracks(source_map: JsonObject) -> list[OpenFiscaTrackManifest]:
    tracks: list[OpenFiscaTrackManifest] = []
    for track in _object_list(source_map.get("tracks", []), "tracks"):
        track_id = _string_value(track.get("track_id"), "track.track_id")
        for oracle_surface in _object_list(
            track.get("oracle_surfaces", []), f"{track_id}.oracle_surfaces"
        ):
            if oracle_surface.get("oracle_id") != OPENFISCA_ORACLE_ID:
                continue
            tracks.append(
                {
                    "track_id": track_id,
                    "role": _string_value(
                        oracle_surface.get("role", "comparison oracle"),
                        f"{track_id}.role",
                    ),
                    "files": _string_list(
                        oracle_surface.get("files", []), f"{track_id}.files"
                    ),
                    "canonical_law": False,
                    "authority": "comparison_oracle",
                }
            )
    return tracks


def build_openfisca_reference_manifest(root: Path) -> OpenFiscaReferenceManifest:
    """Build a guarded OpenFisca comparison-reference manifest.

    OpenFisca references are useful for parity checks and fixture extraction,
    but official NZ source law remains canonical. The returned manifest keeps
    the pinned oracle commit and marks every record as non-authoritative.
    """
    oracle_index = _load_json_object(root / "data" / "oracles" / "oracle-index.json")
    source_map = _load_json_object(
        root / "data" / "coverage" / "tax-benefit-source-map.json"
    )
    oracle = _find_openfisca_oracle(oracle_index)
    tracks = _openfisca_tracks(source_map)

    return {
        "adapter": "openfisca-aotearoa-reference-intake",
        "canonical_law": False,
        "authority": "comparison_oracle",
        "oracle": oracle,
        "tracks": tracks,
    }
