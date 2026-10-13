from __future__ import annotations

# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

import functools
import json
import re
import shutil
import subprocess
from collections import Counter
from functools import cache
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
COUNTRY = "nz"
JURISDICTION_DIR_RE = re.compile(r"^nz(?:-[a-z0-9]+)*$")
ATOMIC_CONTENT_DIRS = ("legislation", "policies", "regulations", "statutes")
PROGRAM_CONTENT_DIR = "programs"
FILESYSTEM_CONTENT_DIRS = (*ATOMIC_CONTENT_DIRS, PROGRAM_CONTENT_DIR)
TRUSTED_APPLIED_MANIFEST_SCHEMA = "axiom-encode/applied-rulespec/v5"
IGNORED_DIRS = {".git", ".pixi", ".pytest_cache", ".venv", "__pycache__", "_axiom"}
DISALLOWED_GENERIC_RULE_NAMES = {
    "amount",
    "base",
    "excess",
    "excess_wages",
    "rate",
    "threshold",
    "value",
}


@functools.cache
def jurisdiction_dirs() -> list[Path]:
    return sorted(
        child
        for child in ROOT.iterdir()
        if child.is_dir()
        and not child.is_symlink()
        and JURISDICTION_DIR_RE.match(child.name)
        and any((child / marker).is_dir() for marker in FILESYSTEM_CONTENT_DIRS)
    )


@functools.cache
def rulespec_content_roots() -> list[Path]:
    return [
        jurisdiction / marker
        for jurisdiction in jurisdiction_dirs()
        for marker in ATOMIC_CONTENT_DIRS
        if (jurisdiction / marker).is_dir()
    ]


def allowed_yaml_roots() -> set[str]:
    return {
        ".axiom",
        ".github",
        ".pre-commit-config.yaml",
        "known-dangling.yaml",
        "known-missing-money-atoms.yaml",
        "known-validation-gaps.yaml",
        *(d.name for d in jurisdiction_dirs()),
    }


def _validation_gaps(section: str) -> set[str]:
    path = ROOT / "known-validation-gaps.yaml"
    if not path.exists():
        return set()
    payload = yaml.safe_load(path.read_text()) or {}
    return set(payload.get(section) or [])


def apply_gap_ratchet(section: str, found: list[str]) -> list[str]:
    allowlisted = _validation_gaps(section)
    found_set = set(found)
    problems = [item for item in found if item not in allowlisted]
    problems.extend(
        f"known-validation-gaps.yaml {section} entry is fixed - remove it: {stale}"
        for stale in sorted(allowlisted - found_set)
    )
    return problems


@cache
def iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def git_output(*args: str, stdin: bytes | None = None, repo: Path = ROOT) -> bytes:
    git = shutil.which("git")
    assert git is not None, "git is required for repository layout checks"
    return subprocess.run(  # noqa: S603 - fixed git argv over a local checkout
        [git, "-C", str(repo), *args],
        input=stdin,
        check=True,
        capture_output=True,
    ).stdout


def tracked_files() -> list[str]:
    output = git_output("ls-files", "-z")
    return sorted(name for name in output.decode("utf-8").split("\0") if name)


@cache
def iter_rulespec_files() -> list[Path]:
    files: list[Path] = []
    for root in rulespec_content_roots():
        files.extend(
            path
            for path in root.rglob("*.yaml")
            if not path.name.endswith(".test.yaml")
        )
    return sorted(files)


def canonical_rule_id(path: Path, rule_name: str) -> str:
    relative = path.relative_to(ROOT)
    prefix = relative.parts[0]
    target = Path(*relative.parts[1:]).with_suffix("").as_posix()
    return f"{prefix}:{target}#{rule_name}"


def module_has_source_locator(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    module = payload.get("module")
    if not isinstance(module, dict):
        return False
    source_verification = module.get("source_verification")
    if not isinstance(source_verification, dict):
        return False
    return isinstance(source_verification.get("corpus_citation_path"), str) and bool(
        source_verification["corpus_citation_path"],
    )


def test_has_nz_country_namespace() -> None:
    assert [path.name for path in jurisdiction_dirs()] == ["nz"]


def test_five_filesystem_roots_and_four_atomic_roots_are_distinct() -> None:
    assert set(ATOMIC_CONTENT_DIRS) == {
        "legislation",
        "policies",
        "regulations",
        "statutes",
    }
    assert set(FILESYSTEM_CONTENT_DIRS) == {
        *ATOMIC_CONTENT_DIRS,
        "programs",
    }
    assert all(
        path.relative_to(ROOT).parts[1] != PROGRAM_CONTENT_DIR
        for path in iter_rulespec_files()
    )


def test_json_manifests_parse() -> None:
    for path in sorted((ROOT / "data").rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8-sig"))


def test_treasury_emtr_snapshot_schema() -> None:
    snapshot = json.loads(
        (ROOT / "data/oracles/treasury-emtr-snapshot.json").read_text(),
    )

    assert snapshot["oracle"]["id"] == "treasury-income-explorer"
    assert snapshot["oracle"]["parameter_vintage"] == "TY27_BEFU25"
    assert snapshot["oracle"]["commit"] == "741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b"

    output_columns = snapshot["generator"]["output_columns"]
    assert {"Net_Income", "EMTR", "PTR", "AS_Amount", "WFF_abated"}.issubset(
        output_columns,
    )
    sampled_wages = snapshot["generator"]["sampled_weekly_gross_wage"]
    assert sampled_wages == [0, 160, 250, 370, 555, 740, 1000, 1500]

    assert len(snapshot["scenarios"]) == 4
    for scenario in snapshot["scenarios"]:
        outputs = scenario["sampled_outputs"]
        assert [row["gross_wage1"] for row in outputs] == sampled_wages
        for row in outputs:
            for column in output_columns:
                assert column in row

    single_adult = next(
        scenario
        for scenario in snapshot["scenarios"]
        if scenario["id"] == "single_no_children_area2_no_housing_costs"
    )
    ietc_by_weekly_wage = {
        row["gross_wage1"]: row["IETC_abated"]
        for row in single_adult["sampled_outputs"]
    }
    assert ietc_by_weekly_wage[740] == 9.972603
    assert ietc_by_weekly_wage[1000] == 9.972603


def test_tax_benefit_source_map_references_known_ids() -> None:
    source_map = json.loads(
        (ROOT / "data/coverage/tax-benefit-source-map.json").read_text(),
    )
    backlog = json.loads((ROOT / "data/coverage/full-country-backlog.json").read_text())
    source_spine = json.loads(
        (ROOT / "data/corpus/inventory/nz/source-spine.json").read_text(),
    )
    oracle_index = json.loads((ROOT / "data/oracles/oracle-index.json").read_text())

    track_ids = {track["id"] for track in backlog["tracks"]}
    source_ids = {source["id"] for source in source_spine["sources"]}
    oracle_ids = {oracle["id"] for oracle in oracle_index["oracles"]}

    unknown_tracks = [
        track["track_id"]
        for track in source_map["tracks"]
        if track["track_id"] not in track_ids
    ]
    unknown_sources = [
        f"{track['track_id']}:{source['source_id']}"
        for track in source_map["tracks"]
        for source in track["official_source_refs"]
        if source["source_id"] not in source_ids
    ]
    unknown_oracles = [
        f"{track['track_id']}:{oracle['oracle_id']}"
        for track in source_map["tracks"]
        for oracle in track["oracle_surfaces"]
        if oracle["oracle_id"] not in oracle_ids
    ]

    assert unknown_tracks == []
    assert unknown_sources == []
    assert unknown_oracles == []


def test_no_obsolete_formula_artifacts() -> None:
    obsolete_ext = ".rac"
    obsolete = [
        path.relative_to(ROOT).as_posix()
        for path in iter_repo_files()
        if path.name.endswith(obsolete_ext)
        or path.name.endswith(f"{obsolete_ext}.test")
        or path.name in {"parameters.yaml", "tests.yaml"}
    ]

    assert obsolete == []


# axiom-encode's trusted git wrapper (axiom-encode#1456) refuses any file that
# carries one of these attributes, so guard-generated aborts before validating.
WORKTREE_TRANSFORMING_ATTRIBUTES = frozenset(
    {"crlf", "eol", "filter", "ident", "text", "working-tree-encoding"},
)
# `binary` is git's built-in macro for `-diff -merge -text`.
REFUSED_GITATTRIBUTES_NAMES = WORKTREE_TRANSFORMING_ATTRIBUTES | {"binary"}


# git splits attribute lines on these four ASCII characters only (attr.c `blank`).
GIT_ATTRIBUTE_BLANKS = " \t\r\n"
GIT_SIMPLE_ESCAPES = frozenset('abfnrtv\\"')


def git_attribute_fields(text: str) -> list[str]:
    return [field for field in re.split(r"[ \t\r\n]+", text) if field]


def quoted_pattern_end(text: str) -> int | None:
    """Return the index of the closing quote if `text` opens a valid C-quoted pattern.

    git unquotes the pattern only when every escape is valid (unquote_c_style:
    one of the single-character escapes, or three octal digits from 000 to 377);
    otherwise it reads the line as an unquoted pattern.
    """
    index = 1
    while index < len(text):
        char = text[index]
        if char == '"':
            return index
        if char == "\\":
            escape = text[index + 1 : index + 2]
            if escape in GIT_SIMPLE_ESCAPES:
                index += 2
                continue
            octal = text[index + 1 : index + 4]
            if re.fullmatch(r"[0-3][0-7][0-7]", octal):
                index += 4
                continue
            return None
        index += 1
    return None


def gitattributes_line_attributes(line: str) -> list[str]:
    """Return the attribute tokens that follow the pattern on one line."""
    text = line.strip(GIT_ATTRIBUTE_BLANKS)
    if not text or text.startswith("#"):
        return []
    if text.startswith('"'):
        end = quoted_pattern_end(text)
        if end is not None:
            return git_attribute_fields(text[end + 1 :])
    return git_attribute_fields(text)[1:]


def gitattributes_file_lines(content: str) -> list[str]:
    # git skips a UTF-8 byte-order mark at the start of the file only, and splits
    # lines on "\n" alone (Python's splitlines also breaks on U+2028 and others).
    return content.removeprefix("\ufeff").split("\n")


def refused_gitattributes_tokens(line: str) -> list[str]:
    """Return the tokens on one line that set or unset a refused attribute.

    `!name` leaves the attribute unspecified, which the wrapper accepts.
    A macro definition (`[attr]name ...`) is checked like any other line.
    """
    return [
        token
        for token in gitattributes_line_attributes(line)
        if not token.startswith("!")
        and token.removeprefix("-").split("=", 1)[0] in REFUSED_GITATTRIBUTES_NAMES
    ]


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("* text=auto eol=lf", ["text=auto", "eol=lf"]),
        ("*.png binary", ["binary"]),
        ("*.pdf -text", ["-text"]),
        ("[ab].png -text", ["-text"]),
        ('"future image.png" filter=lfs', ["filter=lfs"]),
        ('"quoted \\"name\\".png" ident', ["ident"]),
        ("future\\?.png crlf", ["crlf"]),
        ("[attr]mine -diff -text", ["-text"]),
        ("*.md working-tree-encoding=UTF-16", ["working-tree-encoding=UTF-16"]),
        ("*.png -diff -merge", []),
        ('"notes text eol.md" -diff', []),
        ('"a \\" text b.md" -diff', []),
        ('"unterminated -text', ["-text"]),
        ('"abc\\q text diff=x" -diff', ["text"]),
        ('"abc\\777 text diff=x" -diff', ["text"]),
        ('"a\\tb.md" text', ["text"]),
        ('"a\\101 text b.md" -diff', []),
        ("\u00a0 text", ["text"]),
        ("\u2003 text", ["text"]),
        ("*.md\u2028 text", ["text"]),
        ("*.md\ttext", ["text"]),
        ("*.md text=", ["text="]),
        ("*.md !text !eol", []),
        ("*.md !binary", []),
        ("*.md Text", []),
        ("*.txt textual", []),
        ("# * text=auto", []),
        ("", []),
        ("   ", []),
        ("*.png", []),
    ],
)
def test_refused_gitattributes_tokens(line: str, expected: list[str]) -> None:
    assert refused_gitattributes_tokens(line) == expected


@pytest.mark.parametrize(
    ("content", "witness"),
    [
        ("* text=auto eol=lf", "notes.md"),
        ("*.png binary", "image.png"),
        ("*.pdf -text", "paper.pdf"),
        ("[ab].png -text", "a.png"),
        ('"future image.png" filter=lfs', "future image.png"),
        ("future\\?.png crlf", "future?.png"),
        ("[attr]mine -diff -text\n*.bin mine", "blob.bin"),
        ("*.md working-tree-encoding=UTF-16", "notes.md"),
        ("*.txt ident", "notes.txt"),
        ("*.png -diff -merge", "image.png"),
        ('"notes text eol.md" -diff', "notes text eol.md"),
        ('"a \\" text b.md" -diff', 'a " text b.md'),
        ('"unterminated -text', '"unterminated'),
        ('"abc\\q text diff=x" -diff', '"abcq'),
        ('"abc\\777 text diff=x" -diff', '"abc777'),
        ('"a\\tb.md" text', "a\tb.md"),
        ("\u00a0 text", "\u00a0"),
        ("\u2003 text", "\u2003"),
        ("*.md\u2028 text", "a.md\u2028"),
        ('"a\\101 text b.md" -diff', "aA text b.md"),
        ("\ufeff* text", "notes.md"),
        ("\ufeff text", "text"),
        ("*.md -diff\n\ufeff text", "\ufeff"),
        ("*.md\ttext", "notes.md"),
        ("*.md text=", "notes.md"),
        ("*.md !binary", "notes.md"),
        ("*.md Text", "notes.md"),
        ('"\\052.md" text', "notes.md"),
        ("*.md !text !eol", "notes.md"),
        ("*.txt textual", "notes.txt"),
        ("# * text=auto", "notes.md"),
    ],
)
def test_line_check_agrees_with_git_on_a_matching_path(
    tmp_path: Path,
    content: str,
    witness: str,
) -> None:
    """Differential check: the line parser against git's own attribute lookup."""
    # An empty template keeps a configured init template's info/attributes out.
    git_output("init", "--quiet", "--template=", repo=tmp_path)
    (tmp_path / ".gitattributes").write_bytes(f"{content}\n".encode())
    output = git_output(
        "-c",
        "core.attributesFile=/dev/null",
        "check-attr",
        "-z",
        "--all",
        "--",
        witness,
        repo=tmp_path,
    )
    reported = set(output.decode("utf-8").split("\0")[1::3])
    git_refuses = bool(reported & WORKTREE_TRANSFORMING_ATTRIBUTES)
    line_refuses = any(
        refused_gitattributes_tokens(line) for line in gitattributes_file_lines(content)
    )

    assert line_refuses == git_refuses


def test_no_gitattributes_line_sets_a_worktree_transforming_attribute() -> None:
    # Reads every tracked .gitattributes file, so a line is caught before any
    # file matches it and whatever the shape of its pattern.
    refused = [
        f"{name}:{number}: {token}"
        for name in tracked_files()
        if Path(name).name == ".gitattributes"
        for number, line in enumerate(
            gitattributes_file_lines((ROOT / name).read_text(encoding="utf-8")),
            start=1,
        )
        for token in refused_gitattributes_tokens(line)
    ]

    assert refused == []


def test_no_tracked_file_carries_a_worktree_transforming_attribute() -> None:
    output = git_output(
        "-c",
        "core.attributesFile=/dev/null",
        "check-attr",
        "-z",
        "--stdin",
        "--all",
        stdin="\0".join(tracked_files()).encode("utf-8"),
    )
    fields = output.decode("utf-8").split("\0")
    refused = sorted(
        f"{path}: {attribute}"
        for path, attribute in zip(fields[0::3], fields[1::3], strict=False)
        if attribute in WORKTREE_TRANSFORMING_ATTRIBUTES
    )

    assert refused == []


def test_tracked_text_files_use_lf_line_endings() -> None:
    # With no text/eol attribute, git no longer normalises line endings on commit.
    carriage_returns = []
    for name in tracked_files():
        data = (ROOT / name).read_bytes()
        if b"\0" not in data and b"\r" in data:
            carriage_returns.append(name)

    assert carriage_returns == []


def test_no_disallowed_roots_or_yaml_fixtures() -> None:
    jurisdiction_roots = jurisdiction_dirs()
    disallowed_roots = [
        name
        for name in FILESYSTEM_CONTENT_DIRS
        if (ROOT / name).exists() or (ROOT / name).is_symlink()
    ]
    disallowed_roots.extend(
        (base / name).relative_to(ROOT).as_posix()
        for base in jurisdiction_roots
        for name in ("statute", "regulation", "policy", "program")
        if (base / name).exists() or (base / name).is_symlink()
    )
    disallowed_roots.extend(
        child.relative_to(ROOT).as_posix()
        for child in ROOT.iterdir()
        if child.is_dir()
        and (child.is_symlink() or not JURISDICTION_DIR_RE.fullmatch(child.name))
        and any(
            (child / marker).exists() or (child / marker).is_symlink()
            for marker in FILESYSTEM_CONTENT_DIRS
        )
    )
    yaml_fixtures = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "tests").rglob("*.yaml")
        if (ROOT / "tests").exists()
    ]
    allowed = allowed_yaml_roots()
    stray_yaml = [
        path.relative_to(ROOT).as_posix()
        for path in iter_repo_files()
        if path.suffix in {".yaml", ".yml"}
        and path.relative_to(ROOT).parts[0] not in allowed
        and path.name != ".pre-commit-config.yaml"
    ]

    assert disallowed_roots == []
    assert yaml_fixtures == []
    assert stray_yaml == []


def test_canonical_content_uses_regular_exact_yaml_files_without_aliases() -> None:
    problems: list[str] = []
    for jurisdiction in jurisdiction_dirs():
        for marker in FILESYSTEM_CONTENT_DIRS:
            content_root = jurisdiction / marker
            if not content_root.exists() and not content_root.is_symlink():
                continue
            if content_root.is_symlink() or not content_root.is_dir():
                problems.append(
                    f"not a regular directory: {content_root.relative_to(ROOT)}",
                )
                continue
            for path in sorted(content_root.rglob("*")):
                relative = path.relative_to(ROOT).as_posix()
                if path.is_symlink():
                    problems.append(f"alias: {relative}")
                elif path.is_file() and path.suffix != ".yaml":
                    problems.append(f"not exact .yaml: {relative}")

    assert problems == []


def test_program_roots_are_declarative_composition_only() -> None:
    problems: list[str] = []
    for jurisdiction in jurisdiction_dirs():
        program_root = jurisdiction / PROGRAM_CONTENT_DIR
        if not program_root.is_dir():
            continue
        for path in sorted(program_root.rglob("*.yaml")):
            relative = path.relative_to(ROOT).as_posix()
            payload = yaml.safe_load(path.read_text()) or {}
            if not isinstance(payload, dict):
                problems.append(f"{relative}: spec root must be a mapping")
                continue
            if payload.get("format") == "rulespec/v1":
                problems.append(f"{relative}: programs are not atomic RuleSpec modules")
            if not isinstance(payload.get("program"), str) or not payload["program"]:
                problems.append(f"{relative}: missing program id")
            if not isinstance(payload.get("period"), str) or not payload["period"]:
                problems.append(f"{relative}: missing period")
            outputs = payload.get("outputs")
            if (
                not isinstance(outputs, list)
                or not outputs
                or not all(isinstance(output, str) for output in outputs)
            ):
                problems.append(f"{relative}: outputs must be a non-empty string list")

    assert problems == []


def test_encoding_manifests_use_only_the_canonical_root_mirror() -> None:
    manifest_root = ROOT / ".axiom" / "encoding-manifests"
    jurisdictions = {path.name for path in jurisdiction_dirs()}
    problems: list[str] = []

    for jurisdiction in jurisdiction_dirs():
        nested = jurisdiction / ".axiom" / "encoding-manifests"
        if nested.exists() or nested.is_symlink():
            problems.append(f"co-located manifest root: {nested.relative_to(ROOT)}")

    for manifest in sorted(manifest_root.rglob("*.json")):
        relative = manifest.relative_to(manifest_root)
        if len(relative.parts) < 3 or relative.parts[0] not in jurisdictions:
            problems.append(f"noncanonical manifest path: {relative.as_posix()}")
            continue
        jurisdiction, source_root = relative.parts[:2]
        if source_root not in ATOMIC_CONTENT_DIRS:
            problems.append(f"non-atomic manifest path: {relative.as_posix()}")
        payload = json.loads(manifest.read_text())
        for applied in payload.get("applied_files", []):
            applied_path = applied.get("path") if isinstance(applied, dict) else None
            if not isinstance(applied_path, str):
                problems.append(f"invalid applied path: {relative.as_posix()}")
                continue
            parts = Path(applied_path).parts
            if (
                len(parts) < 3
                or parts[0] != jurisdiction
                or parts[1] not in ATOMIC_CONTENT_DIRS
                or Path(applied_path).suffix != ".yaml"
                or not (ROOT / applied_path).is_file()
            ):
                problems.append(
                    f"noncanonical applied path in {relative.as_posix()}: {applied_path}",
                )

    assert problems == []


def test_applied_manifests_use_trusted_v5_schema() -> None:
    manifest_root = ROOT / ".axiom" / "encoding-manifests"
    schemas = Counter(
        json.loads(path.read_text()).get("schema_version")
        for path in manifest_root.rglob("*.json")
    )

    assert set(schemas) <= {TRUSTED_APPLIED_MANIFEST_SCHEMA}, (
        "only trusted v5 manifests may exist after the hard cut; unsigned "
        f"migration state is represented by an empty manifest tree: {dict(schemas)}"
    )


def test_rulespec_files_have_companion_tests() -> None:
    missing = [
        path.relative_to(ROOT).as_posix()
        for path in iter_rulespec_files()
        if not path.with_name(f"{path.stem}.test.yaml").exists()
    ]

    assert apply_gap_ratchet("missing_companion_tests", missing) == []


def test_companion_tests_have_rulespec_files() -> None:
    orphaned = []
    for root in rulespec_content_roots():
        orphaned.extend(
            path.relative_to(ROOT).as_posix()
            for path in sorted(root.rglob("*.test.yaml"))
            if not path.with_name(f"{path.stem.removesuffix('.test')}.yaml").exists()
        )

    assert orphaned == []


def test_rulespec_files_use_rulespec_v1_shape() -> None:
    invalid: list[str] = []

    for path in iter_rulespec_files():
        payload = yaml.safe_load(path.read_text()) or {}
        if not isinstance(payload, dict):
            invalid.append(f"{path.relative_to(ROOT)}: top-level YAML is not a mapping")
            continue
        if payload.get("format") != "rulespec/v1":
            invalid.append(f"{path.relative_to(ROOT)}: missing format: rulespec/v1")
        rules = payload.get("rules")
        if not isinstance(rules, list) or not rules:
            module = payload.get("module")
            status = module.get("status") if isinstance(module, dict) else None
            if rules == [] and status in {"deferred", "entity_not_supported"}:
                continue
            invalid.append(f"{path.relative_to(ROOT)}: missing non-empty rules list")
            continue
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                invalid.append(
                    f"{path.relative_to(ROOT)}: rules[{index}] is not a mapping",
                )
                continue
            for key in ("name", "kind"):
                if key not in rule:
                    invalid.append(
                        f"{path.relative_to(ROOT)}: rules[{index}] missing {key}",
                    )
            if rule.get("kind") in {"parameter", "derived"} and "versions" not in rule:
                invalid.append(
                    f"{path.relative_to(ROOT)}: rules[{index}] missing versions",
                )

    invalid_paths = sorted({item.split(":", 1)[0] for item in invalid})
    assert apply_gap_ratchet("shape_issues", invalid_paths) == []


def test_rulespec_rules_have_source_metadata() -> None:
    missing: list[str] = []

    for path in iter_rulespec_files():
        payload = yaml.safe_load(path.read_text()) or {}
        rules = payload.get("rules")
        if not isinstance(rules, list):
            continue
        module_source_locator = module_has_source_locator(payload)
        for index, rule in enumerate(rules):
            if not isinstance(rule, dict):
                continue
            name = rule.get("name", f"rules[{index}]")
            if rule.get("kind") in {"data_relation", "source_relation"}:
                continue
            if not rule.get("source"):
                missing.append(f"{path.relative_to(ROOT)}: {name} missing source")
            if not module_source_locator:
                missing.append(
                    f"{path.relative_to(ROOT)}: {name} missing source locator",
                )

    assert missing == []


def test_rulespec_files_use_corpus_source_locators() -> None:
    legacy: list[str] = []

    for path in iter_rulespec_files():
        payload = yaml.safe_load(path.read_text()) or {}
        if isinstance(payload, dict):
            module = payload.get("module")
            if isinstance(module, dict):
                if module.get("source_url"):
                    legacy.append(f"{path.relative_to(ROOT)}: module.source_url")
                source_verification = module.get("source_verification")
                if isinstance(source_verification, dict) and source_verification.get(
                    "source_url",
                ):
                    legacy.append(
                        f"{path.relative_to(ROOT)}: "
                        "module.source_verification.source_url",
                    )
            rules = payload.get("rules")
            if isinstance(rules, list):
                for index, rule in enumerate(rules):
                    if not isinstance(rule, dict) or not rule.get("source_url"):
                        continue
                    name = rule.get("name", f"rules[{index}]")
                    legacy.append(f"{path.relative_to(ROOT)}: {name}.source_url")

    assert legacy == []


def test_rulespec_rule_names_are_specific() -> None:
    vague: list[str] = []

    for path in iter_rulespec_files():
        payload = yaml.safe_load(path.read_text()) or {}
        rules = payload.get("rules")
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            name = rule.get("name")
            if name in DISALLOWED_GENERIC_RULE_NAMES:
                vague.append(f"{path.relative_to(ROOT)}: {name}")

    assert vague == []


def test_derived_rules_are_exercised_by_companion_tests() -> None:
    missing: list[str] = []

    for path in iter_rulespec_files():
        payload = yaml.safe_load(path.read_text()) or {}
        rules = payload.get("rules")
        if not isinstance(rules, list):
            continue
        derived_rule_names = [
            str(rule["name"])
            for rule in rules
            if isinstance(rule, dict)
            and rule.get("kind") == "derived"
            and isinstance(rule.get("name"), str)
        ]

        test_path = path.with_name(f"{path.stem}.test.yaml")
        if not test_path.exists():
            continue
        cases = yaml.safe_load(test_path.read_text()) or []
        covered_outputs: set[str] = set()
        if isinstance(cases, list):
            for case in cases:
                if not isinstance(case, dict):
                    continue
                outputs = case.get("output")
                if isinstance(outputs, dict):
                    covered_outputs.update(str(name) for name in outputs)

        missing.extend(
            f"{path.relative_to(ROOT).as_posix()}#{rule_name}"
            for rule_name in derived_rule_names
            if canonical_rule_id(path, rule_name) not in covered_outputs
        )

    assert apply_gap_ratchet("uncovered_derived_rules", missing) == []
