"""Tests for envault.diff module."""

import pytest
from envault.diff import diff_vars, format_diff, DiffEntry


OLD = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "old_secret"}
NEW = {"DB_HOST": "prod.db", "DB_PORT": "5432", "API_KEY": "abc123"}


def test_diff_detects_added_keys():
    entries = diff_vars(OLD, NEW)
    added = [e for e in entries if e.status == "added"]
    assert len(added) == 1
    assert added[0].key == "API_KEY"
    assert added[0].new_value == "abc123"


def test_diff_detects_removed_keys():
    entries = diff_vars(OLD, NEW)
    removed = [e for e in entries if e.status == "removed"]
    assert len(removed) == 1
    assert removed[0].key == "SECRET"
    assert removed[0].old_value == "old_secret"


def test_diff_detects_changed_keys():
    entries = diff_vars(OLD, NEW)
    changed = [e for e in entries if e.status == "changed"]
    assert len(changed) == 1
    assert changed[0].key == "DB_HOST"
    assert changed[0].old_value == "localhost"
    assert changed[0].new_value == "prod.db"


def test_diff_unchanged_excluded_by_default():
    entries = diff_vars(OLD, NEW)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert unchanged == []


def test_diff_show_unchanged_includes_equal_keys():
    entries = diff_vars(OLD, NEW, show_unchanged=True)
    unchanged = [e for e in entries if e.status == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0].key == "DB_PORT"


def test_diff_identical_dicts_returns_empty():
    entries = diff_vars(OLD, OLD)
    assert entries == []


def test_diff_empty_old_all_added():
    entries = diff_vars({}, {"X": "1", "Y": "2"})
    assert all(e.status == "added" for e in entries)
    assert len(entries) == 2


def test_diff_empty_new_all_removed():
    entries = diff_vars({"X": "1"}, {})
    assert entries[0].status == "removed"


def test_format_diff_masks_values_by_default():
    entries = diff_vars(OLD, NEW)
    output = format_diff(entries)
    assert "***" in output
    assert "old_secret" not in output
    assert "abc123" not in output


def test_format_diff_shows_values_when_unmasked():
    entries = diff_vars(OLD, NEW)
    output = format_diff(entries, mask_values=False)
    assert "old_secret" in output
    assert "abc123" in output
    assert "prod.db" in output


def test_format_diff_empty_entries_returns_no_differences():
    output = format_diff([])
    assert output == "No differences found."


def test_format_diff_symbols_present():
    entries = diff_vars(OLD, NEW)
    output = format_diff(entries)
    assert "+" in output
    assert "-" in output
    assert "~" in output
