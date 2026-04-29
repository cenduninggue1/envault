"""Tests for envault snapshot module."""

import pytest
from pathlib import Path

from envault.vault import init_vault, save_vault
from envault.snapshot import (
    SnapshotError,
    create_snapshot,
    restore_snapshot,
    list_snapshots,
    delete_snapshot,
)

PASSWORD = "test-password"


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    init_vault(tmp_path, PASSWORD)
    save_vault(tmp_path, PASSWORD, {"KEY1": "value1", "KEY2": "value2"})
    return tmp_path


def test_create_snapshot_returns_variable_count(vault_dir):
    count = create_snapshot(vault_dir, PASSWORD, "v1")
    assert count == 2


def test_create_snapshot_persists(vault_dir):
    create_snapshot(vault_dir, PASSWORD, "v1")
    snaps = list_snapshots(vault_dir)
    assert len(snaps) == 1
    assert snaps[0]["name"] == "v1"
    assert snaps[0]["count"] == 2


def test_list_snapshots_empty_when_none(vault_dir):
    snaps = list_snapshots(vault_dir)
    assert snaps == []


def test_restore_snapshot_overwrites_current_vars(vault_dir):
    create_snapshot(vault_dir, PASSWORD, "baseline")
    save_vault(vault_dir, PASSWORD, {"KEY1": "changed", "NEW": "extra"})
    count = restore_snapshot(vault_dir, PASSWORD, "baseline")
    assert count == 2
    from envault.vault import load_vault
    restored = load_vault(vault_dir, PASSWORD)
    assert restored == {"KEY1": "value1", "KEY2": "value2"}


def test_restore_snapshot_not_found_raises(vault_dir):
    with pytest.raises(SnapshotError, match="not found"):
        restore_snapshot(vault_dir, PASSWORD, "ghost")


def test_delete_snapshot_removes_entry(vault_dir):
    create_snapshot(vault_dir, PASSWORD, "temp")
    delete_snapshot(vault_dir, "temp")
    snaps = list_snapshots(vault_dir)
    assert all(s["name"] != "temp" for s in snaps)


def test_delete_snapshot_not_found_raises(vault_dir):
    with pytest.raises(SnapshotError, match="not found"):
        delete_snapshot(vault_dir, "nonexistent")


def test_multiple_snapshots_listed(vault_dir):
    create_snapshot(vault_dir, PASSWORD, "snap_a")
    save_vault(vault_dir, PASSWORD, {"ONLY": "one"})
    create_snapshot(vault_dir, PASSWORD, "snap_b")
    snaps = list_snapshots(vault_dir)
    names = [s["name"] for s in snaps]
    assert "snap_a" in names
    assert "snap_b" in names


def test_snapshot_created_at_is_populated(vault_dir):
    create_snapshot(vault_dir, PASSWORD, "timestamped")
    snaps = list_snapshots(vault_dir)
    assert snaps[0]["created_at"] != ""
    assert "T" in snaps[0]["created_at"]
