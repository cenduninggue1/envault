"""Tests for envault.lock."""

from __future__ import annotations

import pytest

from envault.lock import (
    LockError,
    assert_unlocked,
    is_locked,
    lock_info,
    lock_vault,
    unlock_vault,
)


@pytest.fixture()
def vault_dir(tmp_path):
    return tmp_path


def test_lock_vault_creates_lock_file(vault_dir):
    lock_vault(vault_dir, reason="maintenance")
    assert (vault_dir / ".vault.lock").exists()


def test_lock_vault_returns_metadata(vault_dir):
    meta = lock_vault(vault_dir, reason="deploy")
    assert "locked_at" in meta
    assert meta["reason"] == "deploy"


def test_lock_vault_empty_reason_allowed(vault_dir):
    meta = lock_vault(vault_dir)
    assert meta["reason"] == ""


def test_lock_vault_raises_if_already_locked(vault_dir):
    lock_vault(vault_dir, reason="first")
    with pytest.raises(LockError, match="already locked"):
        lock_vault(vault_dir, reason="second")


def test_unlock_vault_removes_lock_file(vault_dir):
    lock_vault(vault_dir)
    unlock_vault(vault_dir)
    assert not (vault_dir / ".vault.lock").exists()


def test_unlock_vault_raises_if_not_locked(vault_dir):
    with pytest.raises(LockError, match="not locked"):
        unlock_vault(vault_dir)


def test_is_locked_false_initially(vault_dir):
    assert is_locked(vault_dir) is False


def test_is_locked_true_after_lock(vault_dir):
    lock_vault(vault_dir)
    assert is_locked(vault_dir) is True


def test_is_locked_false_after_unlock(vault_dir):
    lock_vault(vault_dir)
    unlock_vault(vault_dir)
    assert is_locked(vault_dir) is False


def test_lock_info_returns_none_when_unlocked(vault_dir):
    assert lock_info(vault_dir) is None


def test_lock_info_returns_metadata_when_locked(vault_dir):
    lock_vault(vault_dir, reason="ci")
    info = lock_info(vault_dir)
    assert info is not None
    assert info["reason"] == "ci"
    assert "locked_at" in info


def test_assert_unlocked_passes_when_not_locked(vault_dir):
    assert_unlocked(vault_dir)  # should not raise


def test_assert_unlocked_raises_when_locked(vault_dir):
    lock_vault(vault_dir, reason="readonly")
    with pytest.raises(LockError, match="Vault is locked"):
        assert_unlocked(vault_dir)
