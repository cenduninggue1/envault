"""TTL (time-to-live) support for vault variables."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault


class TTLError(Exception):
    """Raised when a TTL operation fails."""


@dataclass
class TTLEntry:
    key: str
    expires_at: float  # unix timestamp

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at

    @property
    def seconds_remaining(self) -> float:
        return max(0.0, self.expires_at - time.time())


def _get_ttl_store(vault_dir: str, password: str) -> Dict[str, float]:
    """Return the ttl sub-dict from the vault, creating it if absent."""
    data = load_vault(vault_dir, password)
    return data.get("_ttl", {})


def set_ttl(vault_dir: str, password: str, key: str, seconds: float) -> TTLEntry:
    """Attach a TTL to *key*. Raises TTLError if the key does not exist."""
    data = load_vault(vault_dir, password)
    if key not in data.get("vars", {}):
        raise TTLError(f"Variable '{key}' does not exist in the vault.")
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    expires_at = time.time() + seconds
    data.setdefault("_ttl", {})[key] = expires_at
    save_vault(vault_dir, password, data)
    return TTLEntry(key=key, expires_at=expires_at)


def remove_ttl(vault_dir: str, password: str, key: str) -> bool:
    """Remove the TTL for *key*. Returns True if a TTL was present."""
    data = load_vault(vault_dir, password)
    ttl_store: Dict[str, float] = data.get("_ttl", {})
    existed = key in ttl_store
    if existed:
        del ttl_store[key]
        data["_ttl"] = ttl_store
        save_vault(vault_dir, password, data)
    return existed


def list_ttls(vault_dir: str, password: str) -> List[TTLEntry]:
    """Return TTL entries for all keys that have one, sorted by expiry."""
    ttl_store = _get_ttl_store(vault_dir, password)
    entries = [TTLEntry(key=k, expires_at=v) for k, v in ttl_store.items()]
    return sorted(entries, key=lambda e: e.expires_at)


def purge_expired(vault_dir: str, password: str) -> List[str]:
    """Delete variables whose TTL has elapsed. Returns list of purged keys."""
    data = load_vault(vault_dir, password)
    ttl_store: Dict[str, float] = data.get("_ttl", {})
    now = time.time()
    expired = [k for k, exp in ttl_store.items() if now >= exp]
    if not expired:
        return []
    variables: Dict[str, str] = data.get("vars", {})
    for key in expired:
        variables.pop(key, None)
        del ttl_store[key]
    data["vars"] = variables
    data["_ttl"] = ttl_store
    save_vault(vault_dir, password, data)
    return expired
