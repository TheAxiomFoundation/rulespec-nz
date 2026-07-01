import datetime
import json

from pathlib import Path
import pytest

from scripts.phase4_scorecard import generate_scorecard
import scripts.phase4_scorecard as phase4


def test_generate_scorecard_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory_path = tmp_path / "inventory.json"
    scorecard_path = tmp_path / "scorecard.json"

    inventory_data = {
        "modules": [],
        "duplicate_clusters": [],
    }
    inventory_path.write_text(json.dumps(inventory_data), encoding="utf-8-sig")

    monkeypatch.setattr(phase4, "INVENTORY_PATH", inventory_path)
    monkeypatch.setattr(phase4, "SCORECARD_PATH", scorecard_path)

    scorecard = generate_scorecard()

    assert scorecard["total_modules"] == 0
    assert scorecard["modules_with_rules"] == 0
    assert scorecard["modules_deferred"] == 0
    assert scorecard["total_rules"] == 0
    assert scorecard["total_duplicate_clusters"] == 0
    assert scorecard["total_conflicts"] == 0
    assert scorecard["resolved_conflicts"] == 0
    assert scorecard["unresolved_conflicts"] == 0
    assert scorecard["status_view"]["encoded"] == []
    assert scorecard["status_view"]["deferred"] == []
    assert scorecard["status_view"]["blocked"] == []

    # Check that file was written
    assert scorecard_path.exists()
    written_data = json.loads(scorecard_path.read_text(encoding="utf-8"))
    assert written_data == scorecard


def test_generate_scorecard_happy_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory_path = tmp_path / "inventory.json"
    scorecard_path = tmp_path / "scorecard.json"

    inventory_data = {
        "modules": [
            {
                "path": "mod1",
                "rules": [{"id": "r1"}, {"id": "r2"}],
            },
            {
                "path": "mod2",
                "rules": [],
            },
            {
                "path": "mod3",
                # missing "rules" entirely
            },
        ],
        "duplicate_clusters": [
            {
                "conflicts": [
                    {"status": "resolved_official_source"},
                    {"status": "unresolved"},
                ],
            },
            {
                "conflicts": [
                    {"status": "other"},
                ],
            },
        ],
    }
    inventory_path.write_text(json.dumps(inventory_data), encoding="utf-8-sig")

    monkeypatch.setattr(phase4, "INVENTORY_PATH", inventory_path)
    monkeypatch.setattr(phase4, "SCORECARD_PATH", scorecard_path)

    scorecard = generate_scorecard()

    assert scorecard["total_modules"] == 3
    assert scorecard["modules_with_rules"] == 1
    assert scorecard["modules_deferred"] == 2
    assert scorecard["total_rules"] == 2

    assert scorecard["total_duplicate_clusters"] == 2
    assert scorecard["total_conflicts"] == 3
    assert scorecard["resolved_conflicts"] == 1
    assert scorecard["unresolved_conflicts"] == 1

    assert scorecard["status_view"]["encoded"] == ["mod1"]
    # Sorted because the code does sorted() on paths
    assert scorecard["status_view"]["deferred"] == sorted(["mod2", "mod3"])
    assert scorecard["status_view"]["blocked"] == []

    assert scorecard["generated_at"] == str(
        datetime.datetime.now(tz=datetime.UTC).date(),
    )

    # Check that file was written correctly
    assert scorecard_path.exists()
    written_data = json.loads(scorecard_path.read_text(encoding="utf-8"))
    assert written_data == scorecard
