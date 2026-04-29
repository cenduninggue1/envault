"""Vault sharing: export an encrypted bundle and import it on another machine."""

import json
import base64
import os
from typing import Optional

from envault.vault import load_vault, save_vault, init_vault
from envault.crypto import encrypt, decrypt, derive_key


class ShareError(Exception):
    """Raised when a share operation fails."""


def export_bundle(vault_dir: str, password: str, bundle_password: Optional[str] = None) -> str:
    """Export vault variables as a portable encrypted JSON bundle (base64-encoded).

    If *bundle_password* is None the vault password is reused.
    Returns a base64 string suitable for sharing via text / file.
    """
    variables = load_vault(vault_dir, password)
    bundle_password = bundle_password or password

    payload = json.dumps(variables, sort_keys=True).encode()
    token = encrypt(payload, bundle_password)
    bundle = json.dumps({"v": 1, "data": base64.b64encode(token).decode()})
    return base64.b64encode(bundle.encode()).decode()


def import_bundle(
    vault_dir: str,
    bundle: str,
    vault_password: str,
    bundle_password: Optional[str] = None,
    overwrite: bool = False,
) -> int:
    """Import variables from an encrypted bundle into a vault.

    *overwrite* controls whether existing keys are replaced.
    Returns the number of variables written.
    """
    bundle_password = bundle_password or vault_password

    try:
        outer = json.loads(base64.b64decode(bundle).decode())
        if outer.get("v") != 1:
            raise ShareError("Unsupported bundle version.")
        raw_token = base64.b64decode(outer["data"])
    except (KeyError, ValueError, Exception) as exc:
        raise ShareError(f"Malformed bundle: {exc}") from exc

    try:
        payload = decrypt(raw_token, bundle_password)
    except Exception as exc:
        raise ShareError("Failed to decrypt bundle — wrong bundle password?") from exc

    try:
        incoming: dict = json.loads(payload.decode())
    except json.JSONDecodeError as exc:
        raise ShareError(f"Bundle payload is not valid JSON: {exc}") from exc

    vault_path = os.path.join(vault_dir, ".envault")
    if not os.path.exists(vault_path):
        init_vault(vault_dir, vault_password)

    current = load_vault(vault_dir, vault_password)

    if overwrite:
        current.update(incoming)
    else:
        for key, value in incoming.items():
            current.setdefault(key, value)

    save_vault(vault_dir, vault_password, current)
    return len(incoming)
