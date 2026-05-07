"""Profile support: named sets of variables that can be activated together."""

from __future__ import annotations

from typing import Dict, List, Optional

from envault.vault import load_vault, save_vault


class ProfileError(Exception):
    """Raised when a profile operation fails."""


_PROFILES_KEY = "__profiles__"


def _get_profiles(vault_dir: str, password: str) -> Dict[str, Dict[str, str]]:
    data = load_vault(vault_dir, password)
    return data.get(_PROFILES_KEY, {})


def _save_profiles(
    vault_dir: str, password: str, profiles: Dict[str, Dict[str, str]]
) -> None:
    data = load_vault(vault_dir, password)
    data[_PROFILES_KEY] = profiles
    save_vault(vault_dir, password, data)


def create_profile(
    vault_dir: str, password: str, name: str, keys: List[str]
) -> Dict[str, str]:
    """Snapshot the given keys into a named profile."""
    data = load_vault(vault_dir, password)
    variables: Dict[str, str] = {
        k: v for k, v in data.items() if k != _PROFILES_KEY
    }
    missing = [k for k in keys if k not in variables]
    if missing:
        raise ProfileError(f"Unknown variable(s): {', '.join(missing)}")
    snapshot = {k: variables[k] for k in keys}
    profiles = _get_profiles(vault_dir, password)
    profiles[name] = snapshot
    _save_profiles(vault_dir, password, profiles)
    return snapshot


def apply_profile(vault_dir: str, password: str, name: str) -> Dict[str, str]:
    """Merge a profile's variables into the active vault, returning applied vars."""
    profiles = _get_profiles(vault_dir, password)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' does not exist.")
    snapshot = profiles[name]
    data = load_vault(vault_dir, password)
    data.update(snapshot)
    save_vault(vault_dir, password, data)
    return snapshot


def delete_profile(vault_dir: str, password: str, name: str) -> None:
    """Remove a named profile."""
    profiles = _get_profiles(vault_dir, password)
    if name not in profiles:
        raise ProfileError(f"Profile '{name}' does not exist.")
    del profiles[name]
    _save_profiles(vault_dir, password, profiles)


def list_profiles(vault_dir: str, password: str) -> List[str]:
    """Return sorted list of profile names."""
    return sorted(_get_profiles(vault_dir, password).keys())
