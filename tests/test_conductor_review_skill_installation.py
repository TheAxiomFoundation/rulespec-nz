from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".codex" / "skills" / "conductor-review"
SKILL_PATH = SKILL_DIR / "SKILL.md"
REFERENCE_DIR = SKILL_DIR / "references"


def frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, payload, _ = text.split("---", 2)
    parsed = yaml.safe_load(payload)
    assert isinstance(parsed, dict)
    return parsed


@pytest.mark.unit
def test_conductor_review_skill_has_strict_skill_metadata() -> None:
    metadata = frontmatter(SKILL_PATH)

    assert metadata["id"] == "conductor-review"
    assert metadata["name"] == "conductor-review"
    assert metadata["description"]
    assert metadata["version"] == "0.4.1-rulespec-nz.1"
    assert metadata["source"] == "https://github.com/gemini-cli-extensions/conductor"
    assert metadata["source_ref"] == "c9a6a1873ee22fbebfc2e2274ef2e015a8cbdbc0"
    assert "$conductor-review" in metadata["triggers"]
    assert "/conductor:review" in metadata["triggers"]


@pytest.mark.unit
def test_conductor_review_skill_vendors_upstream_review_command() -> None:
    review_command = REFERENCE_DIR / "upstream-review.toml"
    context = REFERENCE_DIR / "upstream-conductor-context.md"
    extension_manifest = REFERENCE_DIR / "upstream-gemini-extension.json"

    assert review_command.exists()
    assert context.exists()
    assert extension_manifest.exists()

    command = tomllib.loads(review_command.read_text(encoding="utf-8"))
    assert command["description"] == (
        "Reviews the completed track work against guidelines and the plan"
    )
    assert "## 2.0 REVIEW PROTOCOL" in command["prompt"]
    assert "## 3.0 COMPLETION PHASE" in command["prompt"]
