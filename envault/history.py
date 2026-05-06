"""Track per-variable change history within a vault."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envault.vault import load_vault, save_vault

_HISTORY_KEY = "__history__"


class HistoryError(Exception):
    """Raised when a history operation fails."""


@dataclass
class HistoryEntry:
    key: str
    old_value: Optional[str]
    new_value: Optional[str]
    action: str  # "set", "delete"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "action": self.action,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            key=data["key"],
            old_value=data.get("old_value"),
            new_value=data.get("new_value"),
            action=data["action"],
            timestamp=data["timestamp"],
        )


def _get_history(vault_vars: dict) -> List[dict]:
    return vault_vars.get(_HISTORY_KEY, [])


def record_change(
    vault_dir: Path,
    password: str,
    key: str,
    old_value: Optional[str],
    new_value: Optional[str],
    action: str = "set",
) -> HistoryEntry:
    """Append a change entry for *key* to the vault's history log."""
    vault_vars = load_vault(vault_dir, password)
    entry = HistoryEntry(
        key=key, old_value=old_value, new_value=new_value, action=action
    )
    history: list = vault_vars.setdefault(_HISTORY_KEY, [])
    history.append(entry.to_dict())
    save_vault(vault_dir, password, vault_vars)
    return entry


def get_history(
    vault_dir: Path, password: str, key: Optional[str] = None
) -> List[HistoryEntry]:
    """Return history entries, optionally filtered by *key*."""
    vault_vars = load_vault(vault_dir, password)
    raw = _get_history(vault_vars)
    entries = [HistoryEntry.from_dict(r) for r in raw]
    if key is not None:
        entries = [e for e in entries if e.key == key]
    return entries


def clear_history(vault_dir: Path, password: str, key: Optional[str] = None) -> int:
    """Clear history entries. If *key* given, only remove entries for that key.

    Returns the number of entries removed.
    """
    vault_vars = load_vault(vault_dir, password)
    raw: list = vault_vars.get(_HISTORY_KEY, [])
    if key is None:
        removed = len(raw)
        vault_vars[_HISTORY_KEY] = []
    else:
        kept = [r for r in raw if r["key"] != key]
        removed = len(raw) - len(kept)
        vault_vars[_HISTORY_KEY] = kept
    save_vault(vault_dir, password, vault_vars)
    return removed
