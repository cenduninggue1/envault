"""Key rotation: re-encrypt vault contents with a new password."""

from pathlib import Path
from typing import Optional

from envault.vault import load_vault, save_vault
from envault.audit import record_event


class RotationError(Exception):
    """Raised when key rotation fails."""


def rotate_key(
    vault_dir: Path,
    old_password: str,
    new_password: str,
    audit: bool = True,
) -> int:
    """Re-encrypt all variables in *vault_dir* with *new_password*.

    Returns the number of variables that were migrated.

    Raises
    ------
    RotationError
        If the old password is wrong or the vault cannot be read/written.
    """
    if not old_password:
        raise RotationError("Old password must not be empty.")
    if not new_password:
        raise RotationError("New password must not be empty.")
    if old_password == new_password:
        raise RotationError("New password must differ from the old password.")

    try:
        variables = load_vault(vault_dir, old_password)
    except Exception as exc:
        raise RotationError(f"Could not decrypt vault with old password: {exc}") from exc

    try:
        save_vault(vault_dir, new_password, variables)
    except Exception as exc:
        raise RotationError(f"Could not save vault with new password: {exc}") from exc

    count = len(variables)

    if audit:
        record_event(
            vault_dir,
            action="rotate_key",
            detail={"variables_migrated": count},
        )

    return count
