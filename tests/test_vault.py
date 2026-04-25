"""Tests for envault.vault module."""

import pathlib
import pytest

from envault.vault import init_vault, load_vault, save_vault


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path / ".envault"


def test_init_vault_creates_file(tmp_vault):
    init_vault("password", tmp_vault)
    assert tmp_vault.exists()


def test_init_vault_raises_if_exists(tmp_vault):
    init_vault("password", tmp_vault)
    with pytest.raises(FileExistsError):
        init_vault("password", tmp_vault)


def test_save_and_load_vault(tmp_vault):
    env_vars = {"API_KEY": "abc123", "DB_URL": "postgres://localhost/db"}
    save_vault(env_vars, "mypassword", tmp_vault)
    loaded = load_vault("mypassword", tmp_vault)
    assert loaded == env_vars


def test_load_vault_wrong_password(tmp_vault):
    save_vault({"KEY": "val"}, "correct", tmp_vault)
    with pytest.raises(ValueError):
        load_vault("wrong", tmp_vault)


def test_load_vault_missing_file(tmp_vault):
    with pytest.raises(FileNotFoundError):
        load_vault("password", tmp_vault)


def test_init_vault_is_empty(tmp_vault):
    init_vault("password", tmp_vault)
    loaded = load_vault("password", tmp_vault)
    assert loaded == {}
