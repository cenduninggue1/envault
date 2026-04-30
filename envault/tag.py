"""Tag management for vault variables — group and filter vars by tag."""

from __future__ import annotations

from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault


class TagError(Exception):
    """Raised when a tag operation fails."""


_TAGS_KEY = "__tags__"


def _get_tags(vault: dict) -> Dict[str, List[str]]:
    """Return the tags mapping {variable_name: [tag, ...]} from vault data."""
    return vault.get(_TAGS_KEY, {})


def add_tag(vault_dir: str, password: str, variable: str, tag: str) -> None:
    """Add *tag* to *variable*. Raises TagError if variable does not exist."""
    data = load_vault(vault_dir, password)
    if variable not in data:
        raise TagError(f"Variable '{variable}' not found in vault.")
    tags: Dict[str, List[str]] = _get_tags(data)
    var_tags = tags.setdefault(variable, [])
    if tag not in var_tags:
        var_tags.append(tag)
    data[_TAGS_KEY] = tags
    save_vault(vault_dir, password, data)


def remove_tag(vault_dir: str, password: str, variable: str, tag: str) -> None:
    """Remove *tag* from *variable*. Raises TagError if tag not present."""
    data = load_vault(vault_dir, password)
    tags: Dict[str, List[str]] = _get_tags(data)
    var_tags = tags.get(variable, [])
    if tag not in var_tags:
        raise TagError(f"Tag '{tag}' not found on variable '{variable}'.")
    var_tags.remove(tag)
    if not var_tags:
        tags.pop(variable, None)
    data[_TAGS_KEY] = tags
    save_vault(vault_dir, password, data)


def list_tags(vault_dir: str, password: str, variable: Optional[str] = None) -> Dict[str, List[str]]:
    """Return tags for *variable*, or all tags if *variable* is None."""
    data = load_vault(vault_dir, password)
    tags = _get_tags(data)
    if variable is not None:
        return {variable: tags.get(variable, [])}
    return {k: v for k, v in tags.items() if k in data}


def filter_by_tag(vault_dir: str, password: str, tag: str) -> Dict[str, str]:
    """Return variables (name→value) that carry *tag*."""
    data = load_vault(vault_dir, password)
    tags = _get_tags(data)
    return {
        var: data[var]
        for var, var_tags in tags.items()
        if tag in var_tags and var in data
    }
