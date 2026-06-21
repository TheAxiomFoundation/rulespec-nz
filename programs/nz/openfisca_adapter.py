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
    source_commit: str
    rulespec_destinations: list[str]
    canonical_law: bool
    authority: str


class PromotedOutputBoundary(TypedDict):
    standalone_yaml_fixtures_allowed: bool
    allowed_roots: list[str]


class FixtureExtractionSchema(TypedDict):
    source_oracle_id: str
    source_commit: str
    canonical_law: bool
    authority: str
    allowed_source_kinds: list[str]
    required_candidate_fields: list[str]
    promoted_output_boundary: PromotedOutputBoundary


class OpenFiscaReferenceManifest(TypedDict):
    adapter: str
    canonical_law: bool
    authority: str
    oracle: OracleManifest
    tracks: list[OpenFiscaTrackManifest]
    fixture_extraction_schema: FixtureExtractionSchema


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


def _rulespec_destinations(track: JsonObject, track_id: str) -> list[str]:
    destinations: list[str] = []
    for batch in _object_list(
        track.get("first_rule_batches", []), f"{track_id}.first_rule_batches"
    ):
        destination = batch.get("destination")
        if isinstance(destination, str):
            destinations.append(destination)
    return destinations


def _openfisca_tracks(
    source_map: JsonObject, oracle: OracleManifest
) -> list[OpenFiscaTrackManifest]:
    tracks: list[OpenFiscaTrackManifest] = []
    for track in _object_list(source_map.get("tracks", []), "tracks"):
        track_id = _string_value(track.get("track_id"), "track.track_id")
        rulespec_destinations = _rulespec_destinations(track, track_id)
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
                    "source_commit": oracle["commit"],
                    "rulespec_destinations": rulespec_destinations,
                    "canonical_law": False,
                    "authority": "comparison_oracle",
                }
            )
    return tracks


def _fixture_extraction_schema(oracle: OracleManifest) -> FixtureExtractionSchema:
    return {
        "source_oracle_id": oracle["id"],
        "source_commit": oracle["commit"],
        "canonical_law": False,
        "authority": "comparison_oracle",
        "allowed_source_kinds": [
            "parameter",
            "test",
            "variable_reference",
        ],
        "required_candidate_fields": [
            "fixture_id",
            "source_kind",
            "source_path",
            "source_commit",
            "track_id",
            "rulespec_destination",
            "inputs",
            "expected_outputs",
            "canonical_law",
            "authority",
        ],
        "promoted_output_boundary": {
            "standalone_yaml_fixtures_allowed": False,
            "allowed_roots": [
                "nz/statutes/",
                "nz/regulations/",
                "nz/policies/",
                "data/oracles/fixtures/openfisca-aotearoa/",
            ],
        },
    }


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
    tracks = _openfisca_tracks(source_map, oracle)

    return {
        "adapter": "openfisca-aotearoa-reference-intake",
        "canonical_law": False,
        "authority": "comparison_oracle",
        "oracle": oracle,
        "tracks": tracks,
        "fixture_extraction_schema": _fixture_extraction_schema(oracle),
    }
