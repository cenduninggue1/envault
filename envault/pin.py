"""Pin/unpin variables to prevent accidental modification or deletion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

PINS_FILENAME = ".envault_pins.json"


class PinError(Exception):
    """Raised when a pin operation fails."""


def _get_pins_path(vault_dir: str) -> Path:
    return Path(vault_dir) / PINS_FILENAME


def _load_pins(vault_dir: str) -> List[str]:
    path = _get_pins_path(vault_dir)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def _save_pins(vault_dir: str, pins: List[str]) -> None:
    path = _get_pins_path(vault_dir)
    with path.open("w", encoding="utf-8") as f:
        json.dump(sorted(set(pins)), f, indent=2)


def pin_var(vault_dir: str, key: str, variables: dict) -> List[str]:
    """Pin a variable key. Raises PinError if the key does not exist."""
    if key not in variables:
        raise PinError(f"Variable '{key}' does not exist in the vault.")
    pins = _load_pins(vault_dir)
    if key not in pins:
        pins.append(key)
    _save_pins(vault_dir, pins)
    return sorted(set(pins))


def unpin_var(vault_dir: str, key: str) -> List[str]:
    """Unpin a variable key. Raises PinError if the key is not pinned."""
    pins = _load_pins(vault_dir)
    if key not in pins:
        raise PinError(f"Variable '{key}' is not pinned.")
    pins = [p for p in pins if p != key]
    _save_pins(vault_dir, pins)
    return sorted(pins)


def list_pins(vault_dir: str) -> List[str]:
    """Return all currently pinned variable keys."""
    return _load_pins(vault_dir)


def is_pinned(vault_dir: str, key: str) -> bool:
    """Return True if the given key is pinned."""
    return key in _load_pins(vault_dir)


def assert_not_pinned(vault_dir: str, key: str, action: str = "modify") -> None:
    """Raise PinError if the key is pinned, blocking the given action."""
    if is_pinned(vault_dir, key):
        raise PinError(
            f"Variable '{key}' is pinned and cannot be {action}d. "
            "Unpin it first with 'envault pin unpin'."
        )
