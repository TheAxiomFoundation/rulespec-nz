"""OpenFisca comparison-oracle intake helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypedDict, cast

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,  # pyright: ignore[reportUnknownVariableType]
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

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


class OpenFiscaSnippet(TypedDict, total=False):
    source_kind: str
    source_path: str
    track_id: str
    value: object
    inputs: JsonObject
    expected_outputs: JsonObject


class FixtureCandidate(TypedDict):
    fixture_id: str
    source_kind: str
    source_path: str
    source_commit: str
    track_id: str
    rulespec_destination: str
    inputs: JsonObject
    expected_outputs: JsonObject
    canonical_law: bool
    authority: str


class OpenFiscaReferenceManifest(TypedDict):
    adapter: str
    canonical_law: bool
    authority: str
    oracle: OracleManifest
    tracks: list[OpenFiscaTrackManifest]
    fixture_extraction_schema: FixtureExtractionSchema


class OpenFiscaSnippetModel(BaseModel):
    """Runtime validation for externally selected OpenFisca snippets."""

    model_config = ConfigDict(extra="forbid", strict=True)

    source_kind: Literal["parameter", "test", "variable_reference"]
    source_path: str
    track_id: str
    value: object | None = None
    inputs: JsonObject = Field(default_factory=dict)
    expected_outputs: JsonObject = Field(default_factory=dict)


class FixtureCandidateModel(BaseModel):
    """Runtime validation for normalized comparison fixture candidates."""

    model_config = ConfigDict(extra="forbid", strict=True)

    fixture_id: str
    source_kind: Literal["parameter", "test", "variable_reference"]
    source_path: str
    source_commit: str
    track_id: str
    rulespec_destination: str
    inputs: JsonObject
    expected_outputs: JsonObject
    canonical_law: bool
    authority: Literal["comparison_oracle"]


def _load_json_object(path: Path) -> JsonObject:
    loaded = cast(object, json.loads(path.read_text(encoding="utf-8")))
    if not isinstance(loaded, dict):
        msg = f"Expected JSON object in {path}"
        raise ValueError(msg)
    return cast(JsonObject, loaded)


def _object_list(value: object, label: str) -> list[JsonObject]:
    if not isinstance(value, list):
        msg = f"Expected list for {label}"
        raise ValueError(msg)
    objects: list[JsonObject] = []
    for index, item in enumerate(cast(list[object], value)):
        if not isinstance(item, dict):
            msg = f"Expected object for {label}[{index}]"
            raise ValueError(msg)
        objects.append(cast(JsonObject, item))
    return objects


def _string_value(value: object, label: str) -> str:
    if not isinstance(value, str):
        msg = f"Expected string for {label}"
        raise ValueError(msg)
    return value


def _object_value(value: object, label: str) -> JsonObject:
    if not isinstance(value, dict):
        msg = f"Expected object for {label}"
        raise ValueError(msg)
    return cast(JsonObject, value)


def _string_list(value: object, label: str) -> list[str]:
    values: list[str] = []
    for index, item in enumerate(_object_or_list_items(value, label)):
        values.append(_string_value(item, f"{label}[{index}]"))
    return values


def _object_or_list_items(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        msg = f"Expected list for {label}"
        raise ValueError(msg)
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
    msg = f"Missing oracle index entry: {OPENFISCA_ORACLE_ID}"
    raise ValueError(msg)


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


def _track_by_id(
    manifest: OpenFiscaReferenceManifest, track_id: str
) -> OpenFiscaTrackManifest:
    for track in manifest["tracks"]:
        if track["track_id"] == track_id:
            return track
    msg = f"Unknown OpenFisca track_id: {track_id}"
    raise ValueError(msg)


def _fixture_name(source_path: str) -> str:
    name = Path(source_path).name
    return name.rsplit(".", maxsplit=1)[0]


def _candidate_outputs(snippet: OpenFiscaSnippet, source_kind: str) -> JsonObject:
    if source_kind == "parameter":
        if "value" not in snippet:
            msg = "Expected value for parameter fixture snippet"
            raise ValueError(msg)
        return {"value": snippet["value"]}
    return _object_value(snippet.get("expected_outputs", {}), "expected_outputs")


def _validated_snippet(snippet: Mapping[str, object], index: int) -> OpenFiscaSnippet:
    try:
        model = OpenFiscaSnippetModel.model_validate(dict(snippet))
    except ValueError as error:
        msg = f"Invalid OpenFisca snippet[{index}]: {error}"
        raise ValueError(msg) from error
    return cast(OpenFiscaSnippet, model.model_dump(exclude_none=True))


def _validated_candidate(candidate: FixtureCandidate) -> FixtureCandidate:
    model = FixtureCandidateModel.model_validate(candidate)
    return cast(FixtureCandidate, model.model_dump())


def build_openfisca_fixture_candidates(
    manifest: OpenFiscaReferenceManifest, snippets: Sequence[Mapping[str, object]]
) -> list[FixtureCandidate]:
    """Normalize selected OpenFisca snippets into comparison fixture candidates.

    The dry-run intentionally returns in-memory candidates only. It carries the
    pinned OpenFisca commit and future RuleSpec destination while preserving the
    comparison-only boundary.
    """
    schema = manifest["fixture_extraction_schema"]
    candidates: list[FixtureCandidate] = []
    for index, raw_snippet in enumerate(snippets):
        snippet = _validated_snippet(raw_snippet, index)
        source_kind = _string_value(
            snippet.get("source_kind"), f"snippet[{index}].source_kind"
        )
        if source_kind not in schema["allowed_source_kinds"]:
            msg = f"Unsupported OpenFisca source_kind: {source_kind}"
            raise ValueError(msg)
        source_path = _string_value(
            snippet.get("source_path"), f"snippet[{index}].source_path"
        )
        track_id = _string_value(snippet.get("track_id"), f"snippet[{index}].track_id")
        track = _track_by_id(manifest, track_id)
        if not track["rulespec_destinations"]:
            msg = f"Missing RuleSpec destination for OpenFisca track: {track_id}"
            raise ValueError(msg)

        candidate: FixtureCandidate = {
            "fixture_id": (
                f"{OPENFISCA_ORACLE_ID}:{track_id}:{source_kind}:"
                f"{_fixture_name(source_path)}"
            ),
            "source_kind": source_kind,
            "source_path": source_path,
            "source_commit": schema["source_commit"],
            "track_id": track_id,
            "rulespec_destination": track["rulespec_destinations"][0],
            "inputs": _object_value(snippet.get("inputs", {}), "inputs"),
            "expected_outputs": _candidate_outputs(snippet, source_kind),
            "canonical_law": False,
            "authority": "comparison_oracle",
        }
        candidates.append(_validated_candidate(candidate))
    return candidates


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
