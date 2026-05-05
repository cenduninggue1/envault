"""Vault locking — temporarily lock a vault to prevent reads or writes."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

LOCK_FILENAME = ".vault.lock"


class LockError(Exception):
    """Raised when a vault lock operation fails."""


def _get_lock_path(vault_dir: str | Path) -> Path:
    return Path(vault_dir) / LOCK_FILENAME


def lock_vault(vault_dir: str | Path, reason: str = "") -> dict:
    """Lock the vault by writing a lock file.

    Returns the lock metadata dict.
    Raises LockError if the vault is already locked.
    """
    lock_path = _get_lock_path(vault_dir)
    if lock_path.exists():
        info = _read_lock(lock_path)
        raise LockError(
            f"Vault is already locked (locked at {info['locked_at']}, reason: {info['reason']!r})"
        )
    metadata = {
        "locked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reason": reason,
    }
    lock_path.write_text(json.dumps(metadata, indent=2))
    return metadata


def unlock_vault(vault_dir: str | Path) -> None:
    """Remove the lock file, unlocking the vault.

    Raises LockError if the vault is not currently locked.
    """
    lock_path = _get_lock_path(vault_dir)
    if not lock_path.exists():
        raise LockError("Vault is not locked.")
    lock_path.unlink()


def is_locked(vault_dir: str | Path) -> bool:
    """Return True if the vault is currently locked."""
    return _get_lock_path(vault_dir).exists()


def lock_info(vault_dir: str | Path) -> Optional[dict]:
    """Return lock metadata if locked, else None."""
    lock_path = _get_lock_path(vault_dir)
    if not lock_path.exists():
        return None
    return _read_lock(lock_path)


def assert_unlocked(vault_dir: str | Path) -> None:
    """Raise LockError if the vault is locked."""
    info = lock_info(vault_dir)
    if info is not None:
        raise LockError(
            f"Vault is locked (locked at {info['locked_at']}, reason: {info['reason']!r}). "
            "Run 'envault lock unlock' to continue."
        )


def _read_lock(lock_path: Path) -> dict:
    try:
        return json.loads(lock_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise LockError(f"Corrupt lock file: {exc}") from exc
