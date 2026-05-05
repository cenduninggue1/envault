"""Tests for envault/cli_ttl.py."""

from __future__ import annotations

import time

import pytest
from click.testing import CliRunner

from envault.cli_ttl import ttl_group
from envault.vault import init_vault, load_vault, save_vault

PASSWORD = "cli-ttl-pass"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_in_tmp(tmp_path):
    init_vault(str(tmp_path), PASSWORD)
    data = load_vault(str(tmp_path), PASSWORD)
    data.setdefault("vars", {})["TOKEN"] = "secret-token"
    save_vault(str(tmp_path), PASSWORD, data)
    return str(tmp_path)


def _invoke(runner, vault_dir, *args):
    return runner.invoke(
        ttl_group,
        list(args),
        obj={"vault_dir": vault_dir},
        catch_exceptions=False,
    )


def test_set_ttl_success(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "set", "TOKEN", "120", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "TTL set" in result.output
    assert "TOKEN" in result.output


def test_set_ttl_unknown_key_fails(runner, vault_in_tmp):
    result = runner.invoke(
        ttl_group,
        ["set", "GHOST", "60", "--password", PASSWORD],
        obj={"vault_dir": vault_in_tmp},
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_remove_ttl_present(runner, vault_in_tmp):
    _invoke(runner, vault_in_tmp, "set", "TOKEN", "60", "--password", PASSWORD)
    result = _invoke(runner, vault_in_tmp, "remove", "TOKEN", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_ttl_absent(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "remove", "TOKEN", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "No TTL" in result.output


def test_list_ttls_empty(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "list", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "No TTLs" in result.output


def test_list_ttls_shows_entry(runner, vault_in_tmp):
    _invoke(runner, vault_in_tmp, "set", "TOKEN", "3600", "--password", PASSWORD)
    result = _invoke(runner, vault_in_tmp, "list", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "TOKEN" in result.output


def test_purge_expired(runner, vault_in_tmp):
    # Plant an already-expired TTL directly
    data = load_vault(vault_in_tmp, PASSWORD)
    data.setdefault("_ttl", {})["TOKEN"] = time.time() - 1
    save_vault(vault_in_tmp, PASSWORD, data)

    result = _invoke(runner, vault_in_tmp, "purge", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "TOKEN" in result.output


def test_purge_nothing(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "purge", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "Nothing to purge" in result.output
