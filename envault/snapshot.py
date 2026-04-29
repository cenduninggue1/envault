"""Snapshot management for envault vaults.

Allows creating named snapshots of the current vault state and restoring
variables from a previous snapshot.
"""

import json
import time
from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


def _get_snapshots_path(vault_dir: Path) -> Path:
    return vault_dir / ".snapshots.json"


def _load_snapshots(vault_dir: Path) -> dict:
    path = _get_snapshots_path(vault_dir)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_snapshots(vault_dir: Path, snapshots: dict) -> None:
    path = _get_snapshots_path(vault_dir)
    with open(path, "w") as f:
        json.dump(snapshots, f, indent=2)


def create_snapshot(vault_dir: Path, password: str, name: str) -> int:
    """Create a named snapshot of the current vault variables.

    Returns the number of variables captured.
    """
    variables = load_vault(vault_dir, password)
    snapshots = _load_snapshots(vault_dir)
    snapshots[name] = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "variables": variables,
    }
    _save_snapshots(vault_dir, snapshots)
    return len(variables)


def restore_snapshot(vault_dir: Path, password: str, name: str) -> int:
    """Restore vault variables from a named snapshot.

    Returns the number of variables restored.
    """
    snapshots = _load_snapshots(vault_dir)
    if name not in snapshots:
        raise SnapshotError(f"Snapshot '{name}' not found.")
    variables = snapshots[name]["variables"]
    save_vault(vault_dir, password, variables)
    return len(variables)


def list_snapshots(vault_dir: Path) -> list[dict]:
    """Return a list of snapshot metadata dicts (name, created_at, count)."""
    snapshots = _load_snapshots(vault_dir)
    return [
        {"name": name, "created_at": data["created_at"], "count": len(data["variables"])}
        for name, data in snapshots.items()
    ]


def delete_snapshot(vault_dir: Path, name: str) -> None:
    """Delete a named snapshot."""
    snapshots = _load_snapshots(vault_dir)
    if name not in snapshots:
        raise SnapshotError(f"Snapshot '{name}' not found.")
    del snapshots[name]
    _save_snapshots(vault_dir, snapshots)
