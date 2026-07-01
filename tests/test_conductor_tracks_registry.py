from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TRACKS_PATH = ROOT / "conductor" / "tracks.md"
TRACKS_DIR = ROOT / "conductor" / "tracks"
ARCHIVE_DIR = TRACKS_DIR / "archive"

TRACK_ENTRY_RE = re.compile(
    r"^## (?P<title>Track .+?|Legacy Track:.+?)\n"
    r"\*Status: (?P<status>.+?)\*\n"
    r"\*Link: \[(?P<label>.+?)\]\((?P<href>.+?)\)\*",
    re.MULTILINE,
)


def tracks_sections() -> tuple[str, str]:
    text = TRACKS_PATH.read_text(encoding="utf-8")
    _, after_active = text.split("## Active Tracks", 1)
    active, archived = after_active.split("## Archived Tracks", 1)
    return active, archived


def track_entries() -> list[re.Match[str]]:
    return list(TRACK_ENTRY_RE.finditer(TRACKS_PATH.read_text(encoding="utf-8")))


@pytest.mark.unit
def test_archived_tracks_are_not_listed_as_active() -> None:
    active, _ = tracks_sections()

    assert "archived" not in active.lower()
    assert "No active tracks." in active


@pytest.mark.unit
def test_track_registry_links_resolve_to_existing_directories() -> None:
    for entry in track_entries():
        href = entry.group("href")
        assert href == entry.group("label")
        target = (ROOT / href).resolve()
        assert target.is_dir(), f"Missing track registry target: {href}"


@pytest.mark.unit
def test_archived_track_registry_entries_point_to_archive() -> None:
    _, archived = tracks_sections()

    for entry in TRACK_ENTRY_RE.finditer(archived):
        status = entry.group("status").lower()
        href = entry.group("href")
        if "archived" in status:
            assert "/archive/" in href, (
                f"Archived track link is outside archive: {href}"
            )


@pytest.mark.unit
def test_no_completed_track_folders_remain_outside_archive() -> None:
    active_track_dirs = [
        child
        for child in TRACKS_DIR.iterdir()
        if child.is_dir() and child.name != "archive"
    ]

    assert active_track_dirs == []


@pytest.mark.unit
def test_archived_track_metadata_matches_folder_ids() -> None:
    for metadata_path in sorted(ARCHIVE_DIR.glob("*/metadata.json")):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        folder_id = metadata_path.parent.name
        if folder_id.startswith("nz_ingest_"):
            continue
        assert metadata["track_id"] == folder_id
        assert "archived" in metadata["status"].lower()
