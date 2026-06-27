import json
import pytest
from pathlib import Path
from typing import Any

from scripts.phase3_reconciliation_workflow import update_clusters


@pytest.fixture
def mock_inventory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    inventory_data = {
        "duplicate_clusters": [
            {
                "id": "income-tax-rate-schedule",
                "other_field": "test_value"
            },
            {
                "id": "main-benefits",
                "other_field": "test_value_3"
            },
            {
                "id": "unknown-cluster-id",
                "other_field": "test_value_2"
            }
        ]
    }

    fake_inventory_path = tmp_path / "rulespec-rule-inventory.json"
    fake_inventory_path.write_text(json.dumps(inventory_data), encoding="utf-8")

    monkeypatch.setattr("scripts.phase3_reconciliation_workflow.INVENTORY_PATH", fake_inventory_path)
    return fake_inventory_path


def test_update_clusters_logic(mock_inventory: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test that update_clusters modifies the inventory and prints the summary."""

    update_clusters()

    # Verify the output
    captured = capsys.readouterr()
    assert f"Updated {mock_inventory}" in captured.out
    assert "Clusters: 3" in captured.out
    assert "Conflicts: 3" in captured.out
    assert "Resolved: 2" in captured.out
    assert "Unresolved: 1" in captured.out

    # Verify the file contents
    updated_data = json.loads(mock_inventory.read_text(encoding="utf-8"))
    clusters = updated_data.get("duplicate_clusters", [])
    assert len(clusters) == 3

    known_cluster = clusters[0]
    assert known_cluster["id"] == "income-tax-rate-schedule"
    assert known_cluster["reconciliation_status"] == "triangulated_with_conflicts"
    assert "reconciliation_surface_links" in known_cluster
    assert len(known_cluster["reconciliation_surface_links"]) > 0
    assert known_cluster["reconciliation_surface_links"][0]["surface_id"] == "income-tax"
    assert "conflicts" in known_cluster
    assert len(known_cluster["conflicts"]) == 1
    assert known_cluster["conflicts"][0]["status"] == "resolved_official_source"

    mb_cluster = clusters[1]
    assert mb_cluster["id"] == "main-benefits"
    assert mb_cluster["reconciliation_status"] == "triangulated_with_conflicts"
    assert "reconciliation_surface_links" in mb_cluster
    assert len(mb_cluster["conflicts"]) == 2
    assert any(c["status"] == "resolved_official_source" for c in mb_cluster["conflicts"])
    assert any(c["status"] == "unresolved" for c in mb_cluster["conflicts"])

    unknown_cluster = clusters[2]
    assert unknown_cluster["id"] == "unknown-cluster-id"
    assert unknown_cluster["reconciliation_status"] == "triangulated_with_conflicts"
    assert "reconciliation_surface_links" in unknown_cluster
    assert unknown_cluster["reconciliation_surface_links"] == []
    assert "conflicts" in unknown_cluster
    assert unknown_cluster["conflicts"] == []
