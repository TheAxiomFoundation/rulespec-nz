#!/usr/bin/env python3
"""Emit GitHub issue payloads for the NZ full-country roadmap."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
ROADMAP_PATH = ROOT / "data" / "coverage" / "full-country-roadmap.json"
BACKLOG_PATH = ROOT / "data" / "coverage" / "full-country-backlog.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def roadmap_entries() -> list[dict[str, Any]]:
    if ROADMAP_PATH.exists():
        roadmap = load_json(ROADMAP_PATH)
        return list(roadmap["roadmap"])
    backlog = load_json(BACKLOG_PATH)
    return [
        {
            "track_id": item["id"],
            "title": item["title"],
            "status": item.get("status", "not_started"),
            "priority": item.get("priority"),
            "administered_by": item.get("administered_by", []),
            "official_source_families": item.get("official_source_families", []),
            "oracle_ids": item.get("oracle_ids", []),
            "components": item.get("components", []),
            "evidence": item.get("evidence", []),
        }
        for item in backlog["tracks"]
    ]


def issue_payload(item: dict[str, Any]) -> dict[str, Any]:
    track_id = str(item.get("track_id") or item["id"])
    title = str(item.get("title") or track_id.replace("-", " ").title())
    labels = ["nz", "roadmap", f"track:{track_id}"]
    if item.get("priority") is not None:
        labels.append(f"priority:{item['priority']}")

    sections = [
        f"Track: `{track_id}`",
        f"Status: `{item.get('status', 'not_started')}`",
    ]
    if item.get("administered_by"):
        sections.append("Administered by: " + ", ".join(item["administered_by"]))
    if item.get("official_source_families"):
        sections.append(
            "Official source families:\n"
            + "\n".join(f"- {source}" for source in item["official_source_families"])
        )
    if item.get("oracle_ids"):
        sections.append(
            "Comparison oracles:\n"
            + "\n".join(f"- {oracle}" for oracle in item["oracle_ids"])
        )
    if item.get("components"):
        sections.append(
            "Components:\n" + "\n".join(f"- {component}" for component in item["components"])
        )
    if item.get("evidence"):
        sections.append(
            "Evidence:\n" + "\n".join(f"- `{path}`" for path in item["evidence"])
        )

    return {
        "track_id": track_id,
        "title": f"NZ roadmap: {title}",
        "labels": labels,
        "body": "\n\n".join(sections),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["gh", "json"], default="gh")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = [issue_payload(item) for item in roadmap_entries()]
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        for item in payload:
            print(json.dumps(item))


if __name__ == "__main__":
    main()
