"""Tests for envault.rotate and envault.cli_rotate."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.vault import init_vault, save_vault, load_vault
from envault.rotate import rotate_key, RotationError
from envault.cli_rotate import rotate_group


@pytest.fixture()
def vault_dir(tmp_path: Path) -> Path:
    init_vault(tmp_path, "old-pass")
    save_vault(tmp_path, "old-pass", {"KEY1": "value1", "KEY2": "value2"})
    return tmp_path


# --- unit tests -----------------------------------------------------------

def test_rotate_key_returns_variable_count(vault_dir: Path) -> None:
    count = rotate_key(vault_dir, "old-pass", "new-pass", audit=False)
    assert count == 2


def test_rotate_key_new_password_works(vault_dir: Path) -> None:
    rotate_key(vault_dir, "old-pass", "new-pass", audit=False)
    data = load_vault(vault_dir, "new-pass")
    assert data == {"KEY1": "value1", "KEY2": "value2"}


def test_rotate_key_old_password_no_longer_works(vault_dir: Path) -> None:
    rotate_key(vault_dir, "old-pass", "new-pass", audit=False)
    with pytest.raises(Exception):
        load_vault(vault_dir, "old-pass")


def test_rotate_key_wrong_old_password_raises(vault_dir: Path) -> None:
    with pytest.raises(RotationError, match="old password"):
        rotate_key(vault_dir, "wrong", "new-pass", audit=False)


def test_rotate_key_same_password_raises(vault_dir: Path) -> None:
    with pytest.raises(RotationError, match="differ"):
        rotate_key(vault_dir, "old-pass", "old-pass", audit=False)


def test_rotate_key_empty_new_password_raises(vault_dir: Path) -> None:
    with pytest.raises(RotationError, match="empty"):
        rotate_key(vault_dir, "old-pass", "", audit=False)


def test_rotate_key_data_unchanged_after_rotation(vault_dir: Path) -> None:
    """Verify that rotation preserves all secret values exactly."""
    original = load_vault(vault_dir, "old-pass")
    rotate_key(vault_dir, "old-pass", "new-pass", audit=False)
    rotated = load_vault(vault_dir, "new-pass")
    assert original == rotated


# --- CLI tests ------------------------------------------------------------

@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def test_cli_rotate_key_success(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["key", "--old-password", "old-pass", "--new-password", "new-pass"],
        obj={"vault_dir": str(vault_dir)},
    )
    assert result.exit_code == 0
    assert "re-encrypted" in result.output


def test_cli_rotate_key_wrong_password(runner: CliRunner, vault_dir: Path) -> None:
    result = runner.invoke(
        rotate_group,
        ["key", "--old-password", "bad", "--new-password", "new-pass"],
        obj={"vault_dir": str(vault_dir)},
    )
    assert result.exit_code != 0
    assert "Error" in result.output


def test_cli_rotate_key_reports_variable_count(runner: CliRunner, vault_dir: Path) -> None:
    """Verify the CLI output mentions the number of re-encrypted variables."""
    result = runner.invoke(
        rotate_group,
        ["key", "--old-password", "old-pass", "--new-password", "new-pass"],
        obj={"vault_dir": str(vault_dir)},
    )
    assert result.exit_code == 0
    assert "2" in result.output
