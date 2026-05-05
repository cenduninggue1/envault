"""Tests for envault/ttl.py."""

from __future__ import annotations

import time

import pytest

from envault.ttl import (
    TTLError,
    TTLEntry,
    list_ttls,
    purge_expired,
    remove_ttl,
    set_ttl,
)
from envault.vault import init_vault, save_vault, load_vault

PASSWORD = "test-secret"


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path), PASSWORD)
    data = load_vault(str(tmp_path), PASSWORD)
    data.setdefault("vars", {})["API_KEY"] = "abc123"
    data["vars"]["DB_URL"] = "postgres://localhost/db"
    save_vault(str(tmp_path), PASSWORD, data)
    return str(tmp_path)


def test_set_ttl_returns_entry(vault_dir):
    entry = set_ttl(vault_dir, PASSWORD, "API_KEY", 60)
    assert isinstance(entry, TTLEntry)
    assert entry.key == "API_KEY"
    assert entry.seconds_remaining > 55


def test_set_ttl_persists(vault_dir):
    set_ttl(vault_dir, PASSWORD, "API_KEY", 120)
    entries = list_ttls(vault_dir, PASSWORD)
    keys = [e.key for e in entries]
    assert "API_KEY" in keys


def test_set_ttl_unknown_key_raises(vault_dir):
    with pytest.raises(TTLError, match="does not exist"):
        set_ttl(vault_dir, PASSWORD, "GHOST", 30)


def test_set_ttl_non_positive_raises(vault_dir):
    with pytest.raises(TTLError, match="positive"):
        set_ttl(vault_dir, PASSWORD, "API_KEY", 0)


def test_remove_ttl_returns_true_when_present(vault_dir):
    set_ttl(vault_dir, PASSWORD, "API_KEY", 60)
    assert remove_ttl(vault_dir, PASSWORD, "API_KEY") is True


def test_remove_ttl_returns_false_when_absent(vault_dir):
    assert remove_ttl(vault_dir, PASSWORD, "API_KEY") is False


def test_list_ttls_sorted_by_expiry(vault_dir):
    set_ttl(vault_dir, PASSWORD, "DB_URL", 200)
    set_ttl(vault_dir, PASSWORD, "API_KEY", 100)
    entries = list_ttls(vault_dir, PASSWORD)
    assert entries[0].key == "API_KEY"
    assert entries[1].key == "DB_URL"


def test_purge_expired_removes_variable(vault_dir):
    # Manually plant an already-expired TTL
    data = load_vault(vault_dir, PASSWORD)
    data.setdefault("_ttl", {})["API_KEY"] = time.time() - 1
    save_vault(vault_dir, PASSWORD, data)

    purged = purge_expired(vault_dir, PASSWORD)
    assert "API_KEY" in purged

    data = load_vault(vault_dir, PASSWORD)
    assert "API_KEY" not in data.get("vars", {})
    assert "API_KEY" not in data.get("_ttl", {})


def test_purge_expired_leaves_live_keys(vault_dir):
    set_ttl(vault_dir, PASSWORD, "API_KEY", 3600)
    purged = purge_expired(vault_dir, PASSWORD)
    assert "API_KEY" not in purged
    data = load_vault(vault_dir, PASSWORD)
    assert "API_KEY" in data.get("vars", {})


def test_purge_nothing_returns_empty(vault_dir):
    assert purge_expired(vault_dir, PASSWORD) == []


def test_ttl_entry_is_expired_flag(vault_dir):
    data = load_vault(vault_dir, PASSWORD)
    data.setdefault("_ttl", {})["DB_URL"] = time.time() - 5
    save_vault(vault_dir, PASSWORD, data)
    entries = list_ttls(vault_dir, PASSWORD)
    expired = [e for e in entries if e.key == "DB_URL"]
    assert expired and expired[0].is_expired
