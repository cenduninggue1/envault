"""Tests for envault.history."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.vault import init_vault
from envault.history import (
    HistoryEntry,
    record_change,
    get_history,
    clear_history,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    init_vault(tmp_path, PASSWORD)
    return tmp_path


def test_record_change_returns_entry(vault_dir: Path) -> None:
    entry = record_change(vault_dir, PASSWORD, "KEY", None, "value", action="set")
    assert isinstance(entry, HistoryEntry)
    assert entry.key == "KEY"
    assert entry.new_value == "value"
    assert entry.old_value is None
    assert entry.action == "set"


def test_record_change_persists(vault_dir: Path) -> None:
    record_change(vault_dir, PASSWORD, "DB_URL", None, "postgres://localhost", action="set")
    entries = get_history(vault_dir, PASSWORD)
    assert len(entries) == 1
    assert entries[0].key == "DB_URL"


def test_multiple_changes_accumulate(vault_dir: Path) -> None:
    record_change(vault_dir, PASSWORD, "FOO", None, "bar", action="set")
    record_change(vault_dir, PASSWORD, "FOO", "bar", "baz", action="set")
    record_change(vault_dir, PASSWORD, "FOO", "baz", None, action="delete")
    entries = get_history(vault_dir, PASSWORD)
    assert len(entries) == 3


def test_get_history_filter_by_key(vault_dir: Path) -> None:
    record_change(vault_dir, PASSWORD, "FOO", None, "1", action="set")
    record_change(vault_dir, PASSWORD, "BAR", None, "2", action="set")
    foo_entries = get_history(vault_dir, PASSWORD, key="FOO")
    assert all(e.key == "FOO" for e in foo_entries)
    assert len(foo_entries) == 1


def test_get_history_empty_when_none(vault_dir: Path) -> None:
    entries = get_history(vault_dir, PASSWORD)
    assert entries == []


def test_clear_history_all(vault_dir: Path) -> None:
    record_change(vault_dir, PASSWORD, "A", None, "1", action="set")
    record_change(vault_dir, PASSWORD, "B", None, "2", action="set")
    removed = clear_history(vault_dir, PASSWORD)
    assert removed == 2
    assert get_history(vault_dir, PASSWORD) == []


def test_clear_history_by_key(vault_dir: Path) -> None:
    record_change(vault_dir, PASSWORD, "A", None, "1", action="set")
    record_change(vault_dir, PASSWORD, "B", None, "2", action="set")
    removed = clear_history(vault_dir, PASSWORD, key="A")
    assert removed == 1
    remaining = get_history(vault_dir, PASSWORD)
    assert len(remaining) == 1
    assert remaining[0].key == "B"


def test_clear_history_returns_zero_when_empty(vault_dir: Path) -> None:
    removed = clear_history(vault_dir, PASSWORD)
    assert removed == 0


def test_history_entry_timestamp_is_set(vault_dir: Path) -> None:
    import time
    before = time.time()
    entry = record_change(vault_dir, PASSWORD, "TS", None, "val", action="set")
    after = time.time()
    assert before <= entry.timestamp <= after


def test_history_entry_roundtrip() -> None:
    entry = HistoryEntry(key="X", old_value="a", new_value="b", action="set", timestamp=1234.0)
    restored = HistoryEntry.from_dict(entry.to_dict())
    assert restored.key == entry.key
    assert restored.old_value == entry.old_value
    assert restored.new_value == entry.new_value
    assert restored.action == entry.action
    assert restored.timestamp == entry.timestamp
