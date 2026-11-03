from __future__ import annotations

import json
import posixpath
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import unquote, urlsplit

import pytest
from markdown_it import MarkdownIt


if TYPE_CHECKING:
    from markdown_it.token import Token


ROOT = Path(__file__).resolve().parents[1]
TRACKS_PATH = ROOT / "conductor" / "tracks.md"
# GitHub resolves relative Markdown links against the file that holds them, so
# every link in tracks.md must resolve from conductor/, not the repository root.
TRACKS_LINK_BASE = TRACKS_PATH.parent
TRACKS_LINK_BASE_NAME = TRACKS_LINK_BASE.relative_to(ROOT).as_posix()
TRACKS_DIR = ROOT / "conductor" / "tracks"
ARCHIVE_DIR = TRACKS_DIR / "archive"

TRACK_ENTRY_RE = re.compile(
    r"^## (?P<title>Track .+?|Legacy Track:.+?)\n"
    r"\*Status: (?P<status>.+?)\*\n"
    r"\*Link: \[(?P<label>.+?)\]\((?P<href>.+?)\)\*",
    re.MULTILINE,
)
# A registry entry links one track directory directly inside the archive.
REGISTRY_HREF_RE = re.compile(r"\./tracks/archive/(?P<track_id>[^/?#\\]+)/")
REGISTRY_HREF_FORM = "./tracks/archive/<id>/, relative to conductor/"

EXTERNAL_SCHEMES = frozenset({"http", "https"})
HTML_LINK_ATTRIBUTES = frozenset({"href", "src"})
# URL-bearing HTML attributes that the link test cannot resolve.
HTML_UNCHECKED_URL_ATTRIBUTES = frozenset(
    {
        "action",
        "background",
        "cite",
        "data",
        "formaction",
        "longdesc",
        "poster",
        "srcset",
        "xlink:href",
    },
)
# Once the parser has consumed every link it can read, a square bracket or a
# tag-like "<" left in plain text marks link syntax that it could not read.
UNPARSED_LINK_RE = re.compile(r"[\[\]]|<\S")


class Link(NamedTuple):
    """A link target in tracks.md and the 1-based line that holds it."""

    line: int
    form: str
    target: str


class Unparsed(NamedTuple):
    """A line in tracks.md that holds link syntax the parser could not read."""

    line: int
    reason: str


class _HtmlLinkCollector(HTMLParser):
    """Collect href and src values, and leftover link syntax, from raw HTML."""

    def __init__(self, first_line: int) -> None:
        super().__init__(convert_charrefs=True)
        self.first_line = first_line
        self.links: list[Link] = []
        self.unparsed: list[Unparsed] = []

    def _line(self) -> int:
        return self.first_line + self.getpos()[0] - 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in HTML_LINK_ATTRIBUTES and value is not None:
                self.links.append(Link(self._line(), f"HTML <{tag} {name}>", value))
            elif name in HTML_LINK_ATTRIBUTES | HTML_UNCHECKED_URL_ATTRIBUTES:
                self.unparsed.append(
                    Unparsed(
                        self._line(),
                        f"HTML <{tag} {name}> the test cannot resolve",
                    ),
                )

    def handle_data(self, data: str) -> None:
        match = UNPARSED_LINK_RE.search(data)
        if match is not None:
            line = self._line() + data.count("\n", 0, match.start())
            self.unparsed.append(
                Unparsed(
                    line,
                    "link syntax inside raw HTML, which GitHub shows as text",
                ),
            )


def _first_line(token: Token) -> int:
    assert token.map is not None, f"markdown-it gave no line map for {token.type}"
    return token.map[0] + 1


def _html_links(html: str, first_line: int) -> tuple[list[Link], list[Unparsed]]:
    collector = _HtmlLinkCollector(first_line)
    collector.feed(html)
    collector.close()
    return collector.links, collector.unparsed


def _inline_links(token: Token) -> tuple[list[Link], list[Unparsed]]:
    links: list[Link] = []
    unparsed: list[Unparsed] = []
    line = _first_line(token)
    for child in token.children or []:
        if child.type == "link_open":
            form = "autolink" if child.markup == "autolink" else "Markdown link"
            links.append(Link(line, form, str(child.attrs["href"])))
        elif child.type == "image":
            links.append(Link(line, "image", str(child.attrs["src"])))
        elif child.type == "html_inline":
            html_links, html_unparsed = _html_links(child.content, line)
            links += html_links
            unparsed += html_unparsed
        elif child.type == "text" and UNPARSED_LINK_RE.search(child.content):
            unparsed.append(Unparsed(line, "link syntax the parser could not read"))
        # Each soft or hard break inside a paragraph starts a new source line.
        line += child.content.count("\n")
        if child.type in {"softbreak", "hardbreak"}:
            line += 1
    return links, unparsed


def extract_links(markdown: str) -> tuple[list[Link], list[Unparsed]]:
    """Return every link in ``markdown`` and each line with syntax it can't read.

    markdown-it-py reads every CommonMark link form: inline links with or
    without a title or ``<...>`` destination, reference-style links and their
    definitions, autolinks, images, and the href or src of raw HTML.
    """
    parser = MarkdownIt("commonmark", {"inline_definitions": True}).enable("table")
    links: list[Link] = []
    unparsed: list[Unparsed] = []
    for token in parser.parse(markdown):
        if token.type == "inline":
            found, unreadable = _inline_links(token)
        elif token.type == "html_block":
            found, unreadable = _html_links(token.content, _first_line(token))
        elif token.type == "definition":
            definition = Link(
                _first_line(token),
                "link reference definition",
                str(token.meta["url"]),
            )
            found, unreadable = [definition], []
        else:
            continue
        links += found
        unparsed += unreadable
    return links, unparsed


def link_problem(target: str) -> str | None:
    """Say why ``target`` does not resolve inside the repo from conductor/."""
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        if parts.scheme in EXTERNAL_SCHEMES and parts.netloc:
            return None
        return "has a scheme or host the test cannot check; use http(s) or a path"
    path = unquote(parts.path)
    if not path:
        # A bare #fragment or ?query points back at tracks.md itself.
        return None
    return _path_problem(path)


def _path_problem(path: str) -> str | None:
    if path.startswith("/") or "\\" in path:
        return "must be a /-separated path relative to conductor/, with no leading /"
    # GitHub turns a path that climbs above the repository root into a broken
    # URL, even if it climbs back in, so check the path before symlinks resolve.
    lexical = posixpath.normpath(posixpath.join(TRACKS_LINK_BASE_NAME, path))
    resolved = (TRACKS_LINK_BASE / path).resolve()
    if lexical.split("/", 1)[0] == ".." or not resolved.is_relative_to(ROOT):
        return f"leaves the repository (it resolves to {resolved})"
    if not resolved.exists():
        return "names nothing that exists, relative to conductor/"
    return None


def tracks_sections() -> tuple[str, str]:
    text = TRACKS_PATH.read_text(encoding="utf-8")
    _, after_active = text.split("## Active Tracks", 1)
    active, archived = after_active.split("## Archived Tracks", 1)
    return active, archived


def track_entries() -> list[re.Match[str]]:
    return list(TRACK_ENTRY_RE.finditer(TRACKS_PATH.read_text(encoding="utf-8")))


def entry_name(entry: re.Match[str]) -> str:
    line = entry.string.count("\n", 0, entry.start("href")) + 1
    return f"conductor/tracks.md:{line} ({entry.group('title')})"


def registry_track_id(href: str) -> str | None:
    """Return the archive directory a registry link names, or None if malformed."""
    match = REGISTRY_HREF_RE.fullmatch(href)
    if match is None or match.group("track_id") in {".", ".."}:
        return None
    return match.group("track_id")


@pytest.mark.unit
def test_archived_tracks_are_not_listed_as_active() -> None:
    active, _ = tracks_sections()

    assert "archived" not in active.lower()
    assert "No active tracks." in active


@pytest.mark.unit
def test_track_registry_links_resolve_to_existing_directories() -> None:
    entries = track_entries()
    assert entries, "No track registry entries parsed from conductor/tracks.md"
    archive = ARCHIVE_DIR.resolve()
    for entry in entries:
        name, href = entry_name(entry), entry.group("href")
        assert href == entry.group("label"), (
            f"{name}: the link text must repeat the link target {href!r}"
        )
        assert registry_track_id(href) is not None, (
            f"{name}: link {href!r} must have the form {REGISTRY_HREF_FORM}, "
            "where <id> names one track directory, never the archive root"
        )
        target = (TRACKS_LINK_BASE / href).resolve()
        assert target.is_dir(), (
            f"{name}: link {href!r} names no directory in conductor/tracks/archive/"
        )
        assert target.parent == archive, (
            f"{name}: link {href!r} resolves to {target}, but a registry entry "
            "must name a directory directly inside conductor/tracks/archive/, "
            "never the archive root"
        )


@pytest.mark.unit
def test_every_archived_track_has_exactly_one_registry_entry() -> None:
    archived = sorted(child.name for child in ARCHIVE_DIR.iterdir() if child.is_dir())
    assert archived, "No track directories found in conductor/tracks/archive/"
    entry_counts = Counter(
        registry_track_id(entry.group("href")) for entry in track_entries()
    )
    missing = [track_id for track_id in archived if entry_counts[track_id] == 0]
    repeated = [track_id for track_id in archived if entry_counts[track_id] > 1]
    assert not missing, (
        "conductor/tracks.md needs one registry entry for each directory in "
        f"conductor/tracks/archive/; these have none: {', '.join(missing)}"
    )
    assert not repeated, (
        "conductor/tracks.md needs exactly one registry entry for each archived "
        f"track; these have more than one: {', '.join(repeated)}"
    )


@pytest.mark.unit
def test_every_link_in_tracks_resolves_inside_repo_from_conductor() -> None:
    text = TRACKS_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    links, unparsed = extract_links(text)
    unreadable = [
        f"  line {spot.line}: {spot.reason}: {lines[spot.line - 1].strip()}"
        for spot in unparsed
    ]
    assert not unreadable, "\n".join(
        [
            "conductor/tracks.md holds link syntax the test cannot parse; fix the "
            "link, or wrap literal brackets in backticks:",
            *unreadable,
        ],
    )
    assert links, "No links parsed from conductor/tracks.md"
    problems = [
        f"  line {link.line}: {link.form} {link.target!r} {problem}"
        for link in links
        if (problem := link_problem(link.target)) is not None
    ]
    assert not problems, "\n".join(
        [
            "Every link in conductor/tracks.md except http(s) links must resolve "
            "inside the repository from conductor/:",
            *problems,
        ],
    )


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
