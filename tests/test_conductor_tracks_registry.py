from __future__ import annotations

import json
import posixpath
import re
from collections import Counter
from html.parser import HTMLParser
from itertools import pairwise
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NamedTuple
from urllib.parse import unquote, urlsplit

import pytest
from markdown_it import MarkdownIt
from markdown_it.parser_inline import ParserInline
from markdown_it.rules_inline import StateInline


if TYPE_CHECKING:
    from markdown_it.token import Token
    from markdown_it.utils import EnvType


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
# Any heading whose rendered text starts like a track heading, at any level.
TRACK_HEADING_RE = re.compile(r"(?:legacy\s+)?track\b", re.IGNORECASE)
TRACK_ENTRY_FORM = (
    "## Track <n>: <title>, then *Status: <status>*, then "
    "*Link: [./tracks/archive/<id>/](./tracks/archive/<id>/)*, with no <...>, "
    "no title and no further line in the entry's paragraph"
)
# A registry entry links one track directory directly inside the archive.
REGISTRY_HREF_RE = re.compile(r"\./tracks/archive/(?P<track_id>[^/?#\\]+)/")
REGISTRY_HREF_FORM = "./tracks/archive/<id>/, relative to conductor/"
# The phrase a registry status line must carry for each status an archived
# track's metadata.json can hold. A bare "archived" adds nothing, so any archived
# status line agrees with it.
REGISTRY_STATUS_PHRASES = {
    "archived": "archived",
    "archived_after_clean_review": "archived after clean review",
    "archived_after_review_remediation": "archived after review remediation",
    "archived_blocked": "blocker",
    "archived_superseded": "archived superseded",
    "archived_with_follow_on_blockers": "archived with follow-on blockers",
}

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
# Browsers trim C0 controls and spaces from both ends of an attribute URL.
URL_TRIM = "".join(map(chr, range(0x21)))
# Once the parser has consumed every link it can read, a square bracket or a
# tag-like "<" left in Markdown text marks link syntax that it could not read.
UNPARSED_LINK_RE = re.compile(r"[\[\]]|<[^\s>]*>|<[A-Za-z/!?]")
# GitHub shows Markdown inside raw HTML as text, so only link shapes count there.
HTML_TEXT_LINK_RE = re.compile(r"\]\(|\]\[|^\s*\[[^\]]+\]:", re.MULTILINE)
# GitHub's GFM 0.29, markdown-it-py's CommonMark 0.31 and browsers disagree on
# declarations, CDATA and processing instructions, so the test refuses them.
HTML_UNPARSABLE_RE = re.compile(r"<!(?!--)|<\?")
# GFM 0.29 opens a raw HTML block at <source>; CommonMark 0.31 does not.
GFM_ONLY_HTML_BLOCK_RE = re.compile(
    r"^ {0,3}</?source(?:[\s/>]|$)",
    re.IGNORECASE | re.MULTILINE,
)
# GitHub turns a bare email address into a mailto: link.
BARE_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# A browser keeps an encoded / or \ inside one path segment.
ENCODED_SEPARATOR_RE = re.compile(r"%(?:2f|5c)", re.IGNORECASE)
CONTROL_CHARACTER_RE = re.compile(r"[\x00-\x1f\x7f]")
# Paths that exist in a checkout but never in the Git tree GitHub serves.
UNTRACKED_PATH_PARTS = frozenset({".git", "__pycache__"})


class Link(NamedTuple):
    """A link target in tracks.md and the 1-based line that holds it."""

    line: int
    form: str
    target: str


class Unparsed(NamedTuple):
    """A line in tracks.md that holds link syntax the parser could not read."""

    line: int
    reason: str


class Registry(NamedTuple):
    """The registry entries GitHub renders, and track headings outside one."""

    entries: list[re.Match[str]]
    stray_headings: list[str]


class _OffsetInlineState(StateInline):
    """Record where each inline token starts in its block's source text."""

    def pushPending(self) -> Token:  # noqa: N802 - markdown-it's method name
        token = super().pushPending()
        token.meta["offset"] = self.pos
        return token

    def push(self, ttype: str, tag: str, nesting: Literal[-1, 0, 1]) -> Token:
        token = super().push(ttype, tag, nesting)
        token.meta["offset"] = self.pos
        return token


class _OffsetParserInline(ParserInline):
    """Parse inline content with _OffsetInlineState."""

    def parse(
        self,
        src: str,
        md: MarkdownIt,
        env: EnvType,
        tokens: list[Token],
    ) -> list[Token]:
        state = _OffsetInlineState(src, md, env, tokens)
        self.tokenize(state)
        for rule in self.ruler2.getRules(""):
            rule(state)
        return state.tokens


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
        # html.unescape silently drops references to control characters, which a
        # browser keeps, so the test refuses numeric references in a URL tag.
        raw_tag = self.get_starttag_text() or ""
        for name, value in attrs:
            if name in HTML_LINK_ATTRIBUTES and "&#" in raw_tag:
                self.unparsed.append(
                    Unparsed(
                        self._line(),
                        "a numeric character reference in a URL tag",
                    ),
                )
            elif name in HTML_LINK_ATTRIBUTES and value is not None:
                form = f"HTML <{tag} {name}>"
                self.links.append(Link(self._line(), form, value.strip(URL_TRIM)))
            elif name in HTML_LINK_ATTRIBUTES | HTML_UNCHECKED_URL_ATTRIBUTES:
                self.unparsed.append(
                    Unparsed(
                        self._line(),
                        f"HTML <{tag} {name}> the test cannot resolve",
                    ),
                )

    def handle_data(self, data: str) -> None:
        match = HTML_TEXT_LINK_RE.search(data)
        if match is not None:
            line = self._line() + data.count("\n", 0, match.start())
            self.unparsed.append(
                Unparsed(
                    line,
                    "Markdown link syntax inside raw HTML, which GitHub shows as text",
                ),
            )


def _markdown_parser() -> MarkdownIt:
    # The commonmark preset's maxNesting of 20 silently drops deeper content.
    parser = MarkdownIt(
        "commonmark",
        {"inline_definitions": True, "maxNesting": 10_000},
    ).enable("table")
    # Keep escapes and entities as text_special tokens, which are literal text.
    parser.disable("text_join")
    offset_inline = _OffsetParserInline()
    offset_inline.ruler = parser.inline.ruler
    offset_inline.ruler2 = parser.inline.ruler2
    parser.inline = offset_inline
    return parser


def _line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _first_line(token: Token) -> int:
    assert token.map is not None, f"markdown-it gave no line map for {token.type}"
    return token.map[0] + 1


def _html_links(html: str, first_line: int) -> tuple[list[Link], list[Unparsed]]:
    collector = _HtmlLinkCollector(first_line)
    unparsable = HTML_UNPARSABLE_RE.search(html)
    if unparsable is not None:
        collector.unparsed.append(
            Unparsed(
                first_line + html.count("\n", 0, unparsable.start()),
                "an HTML declaration, CDATA section or processing instruction",
            ),
        )
    collector.feed(html)
    leftover = collector.rawdata.lstrip()
    if leftover.startswith("<"):
        collector.unparsed.append(
            Unparsed(
                first_line + html.count("\n", 0, len(html) - len(leftover)),
                "an HTML tag or comment left open at the end of the block",
            ),
        )
    collector.close()
    return collector.links, collector.unparsed


def _text_problems(text: str, line: int) -> list[Unparsed]:
    problems: list[Unparsed] = []
    if UNPARSED_LINK_RE.search(text):
        problems.append(Unparsed(line, "link syntax the parser could not read"))
    if BARE_EMAIL_RE.search(text):
        problems.append(Unparsed(line, "a bare email address, which GitHub links"))
    return problems


def _inline_links(token: Token) -> tuple[list[Link], list[Unparsed]]:
    links: list[Link] = []
    unparsed: list[Unparsed] = []
    # Link text can't hold another link, so brackets inside it are only text.
    link_depth = 0
    for child in token.children or []:
        offset = child.meta.get("offset", 0)
        line = _first_line(token) + token.content.count("\n", 0, offset)
        if child.type == "link_open":
            link_depth += 1
            form = "autolink" if child.markup == "autolink" else "Markdown link"
            links.append(Link(line, form, str(child.attrs["href"])))
        elif child.type == "link_close":
            link_depth -= 1
        elif child.type == "image":
            links.append(Link(line, "image", str(child.attrs["src"])))
        elif child.type == "html_inline":
            html_links, html_unparsed = _html_links(child.content, line)
            links += html_links
            unparsed += html_unparsed
        elif child.type == "text" and link_depth == 0:
            unparsed += _text_problems(child.content, line)
    return links, unparsed


def _definition_links(token: Token) -> tuple[list[Link], list[Unparsed]]:
    line = _first_line(token)
    if str(token.meta["label"]).startswith("^"):
        return [], [Unparsed(line, "a GFM footnote, which the test cannot parse")]
    return [Link(line, "link reference definition", str(token.meta["url"]))], []


def extract_links(markdown: str) -> tuple[list[Link], list[Unparsed]]:
    """Return every link in ``markdown`` and each line with syntax it can't read.

    markdown-it-py reads every CommonMark link form: inline links with or
    without a title or ``<...>`` destination, reference-style links and their
    definitions, autolinks, images, and the href or src of raw HTML.
    """
    links: list[Link] = []
    unparsed = [
        Unparsed(_line_of(markdown, match.start()), "a <source> line")
        for match in GFM_ONLY_HTML_BLOCK_RE.finditer(markdown)
    ]
    for token in _markdown_parser().parse(markdown):
        if token.type == "inline":
            found, unreadable = _inline_links(token)
        elif token.type == "html_block":
            found, unreadable = _html_links(token.content, _first_line(token))
        elif token.type == "definition":
            found, unreadable = _definition_links(token)
        else:
            continue
        links += found
        unparsed += unreadable
    return links, unparsed


def link_problem(target: str) -> str | None:
    """Say why ``target`` does not resolve inside the repo from conductor/."""
    try:
        parts = urlsplit(target)
    except ValueError as error:
        return f"is not a URL the test can parse ({error})"
    if parts.scheme or parts.netloc:
        if parts.scheme in EXTERNAL_SCHEMES and parts.netloc:
            return None
        return "has a scheme or host the test cannot check; use http(s) or a path"
    if not parts.path:
        # A bare #fragment or ?query points back at tracks.md itself.
        return None
    return _path_problem(parts.path)


def _path_syntax_problem(raw_path: str, path: str) -> str | None:
    if ENCODED_SEPARATOR_RE.search(raw_path):
        return "encodes / or \\ as %2F or %5C, which a browser keeps in one segment"
    if CONTROL_CHARACTER_RE.search(path):
        return "holds a control character"
    if path.startswith("/") or "\\" in path:
        return "must be a /-separated path relative to conductor/, with no leading /"
    return None


def _path_problem(raw_path: str) -> str | None:
    path = unquote(raw_path)
    syntax_problem = _path_syntax_problem(raw_path, path)
    if syntax_problem is not None:
        return syntax_problem
    # GitHub turns a path that climbs above the repository root into a broken
    # URL, even if it climbs back in, so check the path before symlinks resolve.
    lexical = posixpath.normpath(posixpath.join(TRACKS_LINK_BASE_NAME, path))
    resolved = (TRACKS_LINK_BASE / path).resolve()
    if lexical.split("/", 1)[0] == ".." or not resolved.is_relative_to(ROOT):
        return f"leaves the repository (it resolves to {resolved})"
    if UNTRACKED_PATH_PARTS.intersection(lexical.split("/")):
        return "names a path that Git never tracks"
    if resolved == ARCHIVE_DIR.resolve():
        return "names the archive root; link one track directory inside it"
    if not resolved.exists():
        return "names nothing that exists, relative to conductor/"
    return None


def tracks_sections() -> tuple[str, str]:
    text = TRACKS_PATH.read_text(encoding="utf-8")
    _, after_active = text.split("## Active Tracks", 1)
    active, archived = after_active.split("## Archived Tracks", 1)
    return active, archived


def track_registry() -> Registry:
    """Return the entries GitHub renders, skipping copies in raw HTML or code.

    An entry counts only if GitHub renders its heading as a heading and its
    link as a link. Any rendered track heading outside an entry is stray.
    """
    text = TRACKS_PATH.read_text(encoding="utf-8")
    rendered_links = {
        (link.line, link.target)
        for link in extract_links(text)[0]
        if link.form == "Markdown link"
    }
    tokens = _markdown_parser().parse(text)
    # Map each track heading's line to its rendered text, at any heading level.
    headings: dict[int, str] = {}
    # Lines in the paragraph that follows each track heading.
    paragraph_lines: dict[int, int] = {}
    for index, (opening, inline) in enumerate(pairwise(tokens)):
        title = _rendered_text(inline)
        if opening.type != "heading_open" or not TRACK_HEADING_RE.match(title):
            continue
        line = _first_line(opening)
        headings[line] = title
        following = tokens[index + 3] if index + 3 < len(tokens) else None
        if following is not None and following.type == "paragraph_open":
            assert following.map is not None
            paragraph_lines[line] = following.map[1] - following.map[0]
    entries = [
        entry
        for entry in TRACK_ENTRY_RE.finditer(text)
        if (heading_line := _line_of(text, entry.start())) in headings
        and paragraph_lines.get(heading_line) == 2
        and (_line_of(text, entry.start("href")), entry.group("href")) in rendered_links
    ]
    counted = {_line_of(text, entry.start()) for entry in entries}
    stray = [
        f"line {line} ({title})"
        for line, title in sorted(headings.items())
        if line not in counted
    ]
    return Registry(entries, stray)


def _rendered_text(inline: Token) -> str:
    return "".join(
        child.content
        for child in inline.children or []
        if child.type in {"text", "text_special", "code_inline"}
    )


def entry_name(entry: re.Match[str]) -> str:
    line = _line_of(entry.string, entry.start("href"))
    return f"conductor/tracks.md:{line} ({entry.group('title')})"


def registry_track_id(href: str) -> str | None:
    """Return the archive directory a registry link names, or None if malformed."""
    match = REGISTRY_HREF_RE.fullmatch(href)
    if match is None or match.group("track_id") in {".", ".."}:
        return None
    return match.group("track_id")


def registry_status_problems(
    status_line: str,
    metadata: dict[str, object],
) -> list[str]:
    """Return each way a registry status line misstates its track's metadata.json."""
    problems: list[str] = []
    status = metadata.get("status")
    phrase = REGISTRY_STATUS_PHRASES.get(status) if isinstance(status, str) else None
    if phrase is None:
        problems.append(
            f"metadata.json status {status!r} has no phrase in REGISTRY_STATUS_PHRASES",
        )
    elif phrase not in status_line:
        problems.append(
            f"metadata.json says {status!r}, so the status must say {phrase!r}",
        )
    names_blocker = "blocker" in status_line
    if metadata.get("blockers") and not names_blocker:
        problems.append("metadata.json lists blockers, so the status must name them")
    if names_blocker and not metadata.get("blockers"):
        problems.append("the status names a blocker, but metadata.json lists none")
    return problems


@pytest.mark.unit
def test_archived_tracks_are_not_listed_as_active() -> None:
    active, _ = tracks_sections()

    assert "archived" not in active.lower()
    assert "No active tracks." in active


@pytest.mark.unit
def test_track_registry_links_resolve_to_existing_directories() -> None:
    registry = track_registry()
    assert registry.entries, "No track registry entries parsed from conductor/tracks.md"
    assert not registry.stray_headings, (
        "Each track heading in conductor/tracks.md must start a registry entry of "
        f"the form {TRACK_ENTRY_FORM}. These headings don't: "
        f"{'; '.join(registry.stray_headings)}"
    )
    archive = ARCHIVE_DIR.resolve()
    for entry in registry.entries:
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
        registry_track_id(entry.group("href")) for entry in track_registry().entries
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
        f"  line {spot.line}: {spot.reason}: "
        + (lines[spot.line - 1].strip() if 0 < spot.line <= len(lines) else "")
        for spot in unparsed
    ]
    assert not unreadable, "\n".join(
        [
            "conductor/tracks.md holds link syntax the test cannot parse; fix the "
            "link, or escape literal brackets with a backslash:",
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


@pytest.mark.unit
def test_registry_status_agrees_with_track_metadata() -> None:
    problems: list[str] = []
    for entry in track_registry().entries:
        track_id = registry_track_id(entry.group("href"))
        if track_id is None:
            continue  # test_track_registry_links_resolve_to_existing_directories names it
        metadata_path = ARCHIVE_DIR / track_id / "metadata.json"
        if not metadata_path.is_file():
            problems.append(f"  {entry_name(entry)}: {track_id} has no metadata.json")
            continue
        # Four archived metadata.json files start with a byte-order mark.
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        line = _line_of(entry.string, entry.start("status"))
        problems.extend(
            f"  conductor/tracks.md:{line} ({entry.group('title')}): {problem} "
            f"(it reads {entry.group('status')!r})"
            for problem in registry_status_problems(entry.group("status"), metadata)
        )
    assert not problems, "\n".join(
        [
            "Each registry status in conductor/tracks.md must agree with the status "
            "and blockers in its track's metadata.json:",
            *problems,
        ],
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    ("status_line", "metadata", "expected"),
    [
        (
            "archived after clean review",
            {"status": "archived_after_clean_review", "blockers": []},
            [],
        ),
        (
            "archived after clean review",
            {"status": "archived_with_follow_on_blockers", "blockers": ["open"]},
            ["so the status must say", "so the status must name them"],
        ),
        (
            "archived after clean review",
            {"status": "archived", "blockers": ["open"]},
            ["so the status must name them"],
        ),
        (
            "archived with a blocker",
            {"status": "archived"},
            ["but metadata.json lists none"],
        ),
        (
            "archived after clean review",
            {"status": "archived_after_review_remediation"},
            ["so the status must say"],
        ),
        ("archived", {"status": "archived_pending"}, ["has no phrase"]),
        ("archived", {"status": ["archived"]}, ["has no phrase"]),
    ],
)
def test_registry_status_problems_name_each_disagreement(
    status_line: str,
    metadata: dict[str, object],
    expected: list[str],
) -> None:
    problems = registry_status_problems(status_line, metadata)
    assert len(problems) == len(expected), problems
    for problem, fragment in zip(problems, expected, strict=True):
        assert fragment in problem, (fragment, problem)
