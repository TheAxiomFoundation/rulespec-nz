from __future__ import annotations

# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
JURISDICTION_DIR_RE = re.compile(r"^[a-z]{2}(-[a-z0-9-]+)*$")
CONTENT_DIRS = ("statutes", "regulations", "policies", "legislation")
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


def jurisdiction_dirs() -> list[Path]:
    return sorted(
        child
        for child in ROOT.iterdir()
        if child.is_dir()
        and JURISDICTION_DIR_RE.match(child.name)
        and any((child / marker).is_dir() for marker in CONTENT_DIRS)
    )


def rulespec_content_roots() -> list[Path]:
    return [
        jurisdiction / marker
        for jurisdiction in jurisdiction_dirs()
        for marker in CONTENT_DIRS
        if (jurisdiction / marker).is_dir()
    ]


def allowed_yaml_roots() -> set[str]:
    return {
        ".github",
        "programs",
        "known-dangling.yaml",
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


def iter_repo_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


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
    if source_verification.get("corpus_citation_path"):
        return True
    citation_paths = source_verification.get("corpus_citation_paths")
    return isinstance(citation_paths, list) and any(citation_paths)


def test_has_nz_country_namespace() -> None:
    assert [path.name for path in jurisdiction_dirs()] == ["nz"]


def test_json_manifests_parse() -> None:
    for path in sorted((ROOT / "data").rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8-sig"))


def test_treasury_emtr_snapshot_schema() -> None:
    snapshot = json.loads(
        (ROOT / "data/oracles/treasury-emtr-snapshot.json").read_text()
    )

    assert snapshot["oracle"]["id"] == "treasury-income-explorer"
    assert snapshot["oracle"]["parameter_vintage"] == "TY27_BEFU25"
    assert snapshot["oracle"]["commit"] == "741a6ca4f5d27b1dc00b43dc395e39ffc4040a4b"

    output_columns = snapshot["generator"]["output_columns"]
    assert {"Net_Income", "EMTR", "PTR", "AS_Amount", "WFF_abated"}.issubset(
        output_columns
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
        (ROOT / "data/coverage/tax-benefit-source-map.json").read_text()
    )
    backlog = json.loads((ROOT / "data/coverage/full-country-backlog.json").read_text())
    source_spine = json.loads(
        (ROOT / "data/corpus/inventory/nz/source-spine.json").read_text()
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


def test_no_disallowed_roots_or_yaml_fixtures() -> None:
    singular_bases = [ROOT, *jurisdiction_dirs()]
    disallowed_roots = [
        (base / name).relative_to(ROOT).as_posix()
        for base in singular_bases
        for name in ("statute", "regulation", "policy")
        if (base / name).exists()
    ]
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
    ]

    assert disallowed_roots == []
    assert yaml_fixtures == []
    assert stray_yaml == []


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
                    f"{path.relative_to(ROOT)}: rules[{index}] is not a mapping"
                )
                continue
            for key in ("name", "kind"):
                if key not in rule:
                    invalid.append(
                        f"{path.relative_to(ROOT)}: rules[{index}] missing {key}"
                    )
            if rule.get("kind") in {"parameter", "derived"} and "versions" not in rule:
                invalid.append(
                    f"{path.relative_to(ROOT)}: rules[{index}] missing versions"
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
                    f"{path.relative_to(ROOT)}: {name} missing source locator"
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
                    "source_url"
                ):
                    legacy.append(
                        f"{path.relative_to(ROOT)}: "
                        "module.source_verification.source_url"
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
