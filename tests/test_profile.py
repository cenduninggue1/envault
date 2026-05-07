"""Tests for envault.profile."""

import pytest

from envault.vault import init_vault, save_vault, load_vault
from envault.profile import (
    ProfileError,
    create_profile,
    apply_profile,
    delete_profile,
    list_profiles,
)

PASSWORD = "test-password"


@pytest.fixture()
def vault_dir(tmp_path):
    init_vault(str(tmp_path), PASSWORD)
    save_vault(
        str(tmp_path),
        PASSWORD,
        {"DB_HOST": "localhost", "DB_PORT": "5432", "API_KEY": "secret"},
    )
    return str(tmp_path)


def test_create_profile_returns_snapshot(vault_dir):
    snap = create_profile(vault_dir, PASSWORD, "dev", ["DB_HOST", "DB_PORT"])
    assert snap == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_create_profile_persists(vault_dir):
    create_profile(vault_dir, PASSWORD, "dev", ["DB_HOST"])
    names = list_profiles(vault_dir, PASSWORD)
    assert "dev" in names


def test_create_profile_unknown_key_raises(vault_dir):
    with pytest.raises(ProfileError, match="Unknown variable"):
        create_profile(vault_dir, PASSWORD, "bad", ["NONEXISTENT"])


def test_list_profiles_empty_when_none(vault_dir):
    assert list_profiles(vault_dir, PASSWORD) == []


def test_list_profiles_sorted(vault_dir):
    create_profile(vault_dir, PASSWORD, "prod", ["API_KEY"])
    create_profile(vault_dir, PASSWORD, "dev", ["DB_HOST"])
    assert list_profiles(vault_dir, PASSWORD) == ["dev", "prod"]


def test_apply_profile_merges_vars(vault_dir):
    create_profile(vault_dir, PASSWORD, "staging", ["DB_HOST"])
    # Overwrite DB_HOST in vault before applying
    save_vault(
        vault_dir,
        PASSWORD,
        {"DB_HOST": "changed", "DB_PORT": "5432", "API_KEY": "secret"},
    )
    applied = apply_profile(vault_dir, PASSWORD, "staging")
    assert applied["DB_HOST"] == "localhost"
    data = load_vault(vault_dir, PASSWORD)
    assert data["DB_HOST"] == "localhost"


def test_apply_profile_unknown_name_raises(vault_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        apply_profile(vault_dir, PASSWORD, "ghost")


def test_delete_profile_removes_it(vault_dir):
    create_profile(vault_dir, PASSWORD, "temp", ["API_KEY"])
    delete_profile(vault_dir, PASSWORD, "temp")
    assert "temp" not in list_profiles(vault_dir, PASSWORD)


def test_delete_profile_unknown_raises(vault_dir):
    with pytest.raises(ProfileError, match="does not exist"):
        delete_profile(vault_dir, PASSWORD, "missing")


def test_multiple_profiles_independent(vault_dir):
    create_profile(vault_dir, PASSWORD, "dev", ["DB_HOST"])
    create_profile(vault_dir, PASSWORD, "prod", ["API_KEY"])
    names = list_profiles(vault_dir, PASSWORD)
    assert set(names) == {"dev", "prod"}
