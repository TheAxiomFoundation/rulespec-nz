#!/usr/bin/env python3
"""Compute the bulk-encode job matrix from bulk/worklist.yaml.

The worklist is the durable queue. This script is the single source of truth for
turning it into a job matrix and for reading entry backend/model/status, so a
local codex drain and any future CI dispatcher behave identically.

Usage:
  python bulk/compute_matrix.py --status pending [--batch A] [--limit 8] --format table
  python bulk/compute_matrix.py --get nz/statute/act/public/2007/0097/section/MD-3 --field model

The matrix shape is {"include": [{"citation", "repo", "backend", "model",
"slug"}, ...]}. `slug` is the branch-safe citation slug used for `bulk/<slug>`
branches and the PR title.

Status writes are intentionally NOT done here by CI: statuses change by
committing to the worklist (a reviewable diff), never silent mutation.
`--set-status` exists only for local operator use and edits the file in place.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

WORKLIST = Path(__file__).resolve().parent / "worklist.yaml"

SELECTABLE_STATUSES = {"pending"}


def citation_slug(citation: str) -> str:
    """Branch-safe slug for a citation path.

    nz/statute/act/public/2007/0097/section/MD-3 -> nz-statute-act-public-2007-0097-section-md-3
    """
    slug = citation.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load() -> dict:
    data = yaml.safe_load(WORKLIST.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict) or "entries" not in data:
        raise SystemExit(f"{WORKLIST} is missing an 'entries' list")
    return data


def entry_backend(data: dict, entry: dict) -> str:
    return entry.get("backend") or data.get("defaults", {}).get("backend", "codex")


def entry_model(data: dict, entry: dict) -> str:
    return entry.get("model") or data.get("defaults", {}).get("model", "gpt-5.5")


def select(data: dict, status: str, batch: str | None, limit: int | None) -> list[dict]:
    out: list[dict] = []
    for entry in data["entries"]:
        if status != "any" and entry.get("status") != status:
            continue
        if batch and str(entry.get("batch", "")).upper() != batch.upper():
            continue
        out.append(
            {
                "citation": entry["citation"],
                "repo": entry.get("repo", "rulespec-nz"),
                "backend": entry_backend(data, entry),
                "model": entry_model(data, entry),
                "slug": citation_slug(entry["citation"]),
            }
        )
    if limit is not None:
        out = out[:limit]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--status", default="pending", help="Entry status to select (or 'any').")
    ap.add_argument("--batch", default=None, help="Restrict to a batch label (A, B, ...).")
    ap.add_argument("--limit", type=int, default=None, help="Cap the number of entries.")
    ap.add_argument(
        "--format",
        choices=["matrix", "table", "count"],
        default="matrix",
        help="matrix = job include JSON; table = human listing; count = number selected.",
    )
    ap.add_argument("--get", default=None, help="Look up a single citation's entry.")
    ap.add_argument("--field", default=None, help="With --get, print one field (model/backend/status/slug).")
    ap.add_argument(
        "--set-status",
        nargs=2,
        metavar=("CITATION", "STATUS"),
        default=None,
        help="LOCAL ONLY: set an entry's status in place.",
    )
    args = ap.parse_args()

    data = load()

    if args.set_status:
        citation, new_status = args.set_status
        found = False
        for entry in data["entries"]:
            if entry["citation"] == citation:
                entry["status"] = new_status
                found = True
                break
        if not found:
            raise SystemExit(f"citation not found: {citation}")
        WORKLIST.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        print(f"set {citation} -> {new_status}")
        return 0

    if args.get:
        for entry in data["entries"]:
            if entry["citation"] == args.get:
                if args.field == "slug":
                    print(citation_slug(entry["citation"]))
                elif args.field == "model":
                    print(entry_model(data, entry))
                elif args.field == "backend":
                    print(entry_backend(data, entry))
                elif args.field:
                    print(entry.get(args.field, ""))
                else:
                    print(json.dumps(entry))
                return 0
        raise SystemExit(f"citation not found: {args.get}")

    selected = select(data, args.status, args.batch, args.limit)

    if args.format == "count":
        print(len(selected))
    elif args.format == "table":
        for item in selected:
            print(f"{item['slug']:52s} {item['backend']}:{item['model']:10s} {item['citation']}")
        print(f"\n{len(selected)} entr{'y' if len(selected) == 1 else 'ies'} selected (status={args.status}).")
    else:
        print(json.dumps({"include": selected}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
