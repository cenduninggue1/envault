"""Vault file management: read, write, and parse encrypted vault files."""

import json
import pathlib
from typing import Dict

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_PATH = pathlib.Path(".envault")


def _load_raw(vault_path: pathlib.Path) -> bytes:
    if not vault_path.exists():
        raise FileNotFoundError(f"Vault not found: {vault_path}")
    return vault_path.read_bytes()


def _save_raw(vault_path: pathlib.Path, data: bytes) -> None:
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    vault_path.write_bytes(data)


def load_vault(password: str, vault_path: pathlib.Path = DEFAULT_VAULT_PATH) -> Dict[str, str]:
    """Load and decrypt a vault file, returning a dict of env vars."""
    raw = _load_raw(vault_path)
    plaintext = decrypt(raw, password)
    return json.loads(plaintext)


def save_vault(
    env_vars: Dict[str, str],
    password: str,
    vault_path: pathlib.Path = DEFAULT_VAULT_PATH,
) -> None:
    """Encrypt and save env vars dict to a vault file."""
    plaintext = json.dumps(env_vars, indent=2)
    raw = encrypt(plaintext, password)
    _save_raw(vault_path, raw)


def init_vault(
    password: str,
    vault_path: pathlib.Path = DEFAULT_VAULT_PATH,
) -> None:
    """Create a new empty vault file."""
    if vault_path.exists():
        raise FileExistsError(f"Vault already exists: {vault_path}")
    save_vault({}, password, vault_path)
