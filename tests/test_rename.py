"""Tests for envault.rename module."""

import pytest

from envault.vault import init_vault, load_vault, save_vault
from envault.rename import RenameError, RenameResult, rename_var, copy_var


PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path), PASSWORD)
    save_vault(str(tmp_path), PASSWORD, {"FOO": "bar", "BAZ": "qux"})
    return str(tmp_path)


def test_rename_var_moves_key(vault_dir):
    result = rename_var(vault_dir, PASSWORD, "FOO", "FOO_NEW")
    assert isinstance(result, RenameResult)
    assert result.old_key == "FOO"
    assert result.new_key == "FOO_NEW"
    assert result.copied is False


def test_rename_var_old_key_removed(vault_dir):
    rename_var(vault_dir, PASSWORD, "FOO", "FOO_NEW")
    variables = load_vault(vault_dir, PASSWORD)
    assert "FOO" not in variables
    assert variables["FOO_NEW"] == "bar"


def test_rename_var_other_keys_unaffected(vault_dir):
    rename_var(vault_dir, PASSWORD, "FOO", "FOO_NEW")
    variables = load_vault(vault_dir, PASSWORD)
    assert variables["BAZ"] == "qux"


def test_rename_var_missing_key_raises(vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        rename_var(vault_dir, PASSWORD, "MISSING", "NEW")


def test_rename_var_collision_raises(vault_dir):
    with pytest.raises(RenameError, match="already exists"):
        rename_var(vault_dir, PASSWORD, "FOO", "BAZ")


def test_rename_var_collision_with_overwrite(vault_dir):
    rename_var(vault_dir, PASSWORD, "FOO", "BAZ", overwrite=True)
    variables = load_vault(vault_dir, PASSWORD)
    assert variables["BAZ"] == "bar"
    assert "FOO" not in variables


def test_rename_var_same_key_raises(vault_dir):
    with pytest.raises(RenameError, match="identical"):
        rename_var(vault_dir, PASSWORD, "FOO", "FOO")


def test_copy_var_keeps_original(vault_dir):
    result = copy_var(vault_dir, PASSWORD, "FOO", "FOO_COPY")
    assert result.copied is True
    variables = load_vault(vault_dir, PASSWORD)
    assert variables["FOO"] == "bar"
    assert variables["FOO_COPY"] == "bar"


def test_copy_var_missing_key_raises(vault_dir):
    with pytest.raises(RenameError, match="does not exist"):
        copy_var(vault_dir, PASSWORD, "MISSING", "DEST")


def test_copy_var_collision_raises(vault_dir):
    with pytest.raises(RenameError, match="already exists"):
        copy_var(vault_dir, PASSWORD, "FOO", "BAZ")


def test_copy_var_collision_with_overwrite(vault_dir):
    copy_var(vault_dir, PASSWORD, "FOO", "BAZ", overwrite=True)
    variables = load_vault(vault_dir, PASSWORD)
    assert variables["BAZ"] == "bar"
    assert variables["FOO"] == "bar"  # original still present


def test_copy_var_same_key_raises(vault_dir):
    with pytest.raises(RenameError, match="identical"):
        copy_var(vault_dir, PASSWORD, "FOO", "FOO")
