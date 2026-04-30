"""Rename or copy variables within a vault."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from envault.vault import load_vault, save_vault


class RenameError(Exception):
    """Raised when a rename or copy operation fails."""


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    copied: bool  # True if original was kept, False if moved


def rename_var(
    vault_dir: str,
    password: str,
    old_key: str,
    new_key: str,
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Rename *old_key* to *new_key* inside the vault (move semantics)."""
    variables = load_vault(vault_dir, password)

    if old_key not in variables:
        raise RenameError(f"Variable '{old_key}' does not exist.")
    if new_key in variables and not overwrite:
        raise RenameError(
            f"Variable '{new_key}' already exists. Use overwrite=True to replace it."
        )
    if old_key == new_key:
        raise RenameError("Old and new key names are identical.")

    variables[new_key] = variables.pop(old_key)
    save_vault(vault_dir, password, variables)
    return RenameResult(old_key=old_key, new_key=new_key, copied=False)


def copy_var(
    vault_dir: str,
    password: str,
    src_key: str,
    dst_key: str,
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Copy *src_key* to *dst_key* inside the vault (original is kept)."""
    variables = load_vault(vault_dir, password)

    if src_key not in variables:
        raise RenameError(f"Variable '{src_key}' does not exist.")
    if dst_key in variables and not overwrite:
        raise RenameError(
            f"Variable '{dst_key}' already exists. Use overwrite=True to replace it."
        )
    if src_key == dst_key:
        raise RenameError("Source and destination key names are identical.")

    variables[dst_key] = variables[src_key]
    save_vault(vault_dir, password, variables)
    return RenameResult(old_key=src_key, new_key=dst_key, copied=True)
