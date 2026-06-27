#!/usr/bin/env python3
"""
Validate and optionally sync NZ full-country roadmap artifacts to GitHub issues.

Usage examples:
  python scripts/nz_full_country_roadmap_sync.py --check
  python scripts/nz_full_country_roadmap_sync.py --format gh --emit-commands
  python scripts/nz_full_country_roadmap_sync.py --create-issues --label-sync
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterable, List

from scripts.nz_full_country_roadmap_export import issue_payload


ROOT = Path(__file__).resolve().parent.parent
ROADMAP_PATH = ROOT / "data" / "coverage" / "full-country-roadmap.json"
BACKLOG_PATH = ROOT / "data" / "coverage" / "full-country-backlog.json"
REPO = "edithatogo/rulespec-nz"


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iterate_tracks(backlog: Dict, roadmap: Dict) -> Iterable[Dict]:
    backlog_map = {item["id"]: item for item in backlog["tracks"]}
    roadmap_map = {item["track_id"]: item for item in roadmap["roadmap"]}
    for track_id in backlog_map.keys():
        yield {
            "id": track_id,
            "backlog": backlog_map[track_id],
            "roadmap": roadmap_map.get(track_id),
        }


def check_coverage() -> int:
    backlog = load_json(BACKLOG_PATH)
    roadmap = load_json(ROADMAP_PATH)

    backlog_ids = {item["id"] for item in backlog["tracks"]}
    roadmap_ids = {item["track_id"] for item in roadmap["roadmap"]}
    missing = sorted(backlog_ids - roadmap_ids)
    extra = sorted(roadmap_ids - backlog_ids)

    failures = 0
    if missing:
        failures += 1
        print(f"Missing roadmap entries: {', '.join(missing)}")
    if extra:
        failures += 1
        print(f"Roadmap tracks not in backlog: {', '.join(extra)}")

    missing_evidence = []
    for track in roadmap["roadmap"]:
        missing_paths: List[str] = []
        for rel in track.get("evidence", []):
            p = ROOT / rel
            if not p.exists():
                missing_paths.append(rel)
        if missing_paths:
            failures += 1
            missing_evidence.append((track["track_id"], missing_paths))

    if missing_evidence:
        for track_id, paths in missing_evidence:
            print(f"Missing evidence files for {track_id}: {', '.join(paths)}")

    if failures:
        print(f"Coverage check failed with {failures} issue(s).")
    else:
        print("Coverage check passed.")
    return failures


def emit_commands() -> None:
    roadmap = load_json(ROADMAP_PATH)
    payload = [issue_payload(item) for item in roadmap["roadmap"]]
    for item in payload:
        title = item["title"]
        body = item["body"].replace("'", "'\"'\"'")
        labels = " ".join([f"--label '{l}'" for l in item["labels"]])
        print(
            f"gh issue create --repo {REPO} --title {title!r} "
            f"--body '{body}' {labels}"
        )


def run_create_issues(label_sync: bool = False) -> int:
    roadmap = load_json(ROADMAP_PATH)
    payload = [issue_payload(item) for item in roadmap["roadmap"]]
    created = 0
    with tempfile.TemporaryDirectory() as tmpdir:
        for item in payload:
            body_file = Path(tmpdir) / f"{item['track_id']}.md"
            body_file.write_text(item["body"], encoding="utf-8")
            args = [
                "gh",
                "issue",
                "create",
                "--repo",
                REPO,
                "--title",
                item["title"],
                "--body-file",
                str(body_file),
            ]
            for label in item["labels"]:
                args.extend(["--label", label])
            if label_sync:
                args.extend(["--label", f"track-id:{item['track_id']}"])
            result = subprocess.run(args, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed for {item['track_id']}: {result.stderr}")
                return 1
            print(f"Created: {result.stdout.strip()}")
            created += 1
    print(f"Created {created} issues.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate roadmap against backlog + evidence files")
    parser.add_argument(
        "--format",
        choices=["gh", "commands"],
        default="gh",
        help="Output format for issue payloads (gh json or shell commands)",
    )
    parser.add_argument("--emit-commands", action="store_true", help="Print gh create commands for dry-run review")
    parser.add_argument("--create-issues", action="store_true", help="Create GitHub issues from roadmap payload")
    parser.add_argument("--label-sync", action="store_true", help="Add track id sync label when creating issues")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.check or not (args.emit_commands or args.create_issues):
        rc = check_coverage()
        if rc:
            raise SystemExit(rc)

    if args.emit_commands:
        emit_commands()

    if args.create_issues:
        if os.environ.get("CI"):
            print("Refusing to create issues in CI context.")
            raise SystemExit(1)
        rc = run_create_issues(label_sync=args.label_sync)
        raise SystemExit(rc)


if __name__ == "__main__":
    main()
