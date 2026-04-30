"""Tests for the CLI tag commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_tag import tag_group
from envault.vault import init_vault, save_vault


PASSWORD = "cli-test-secret"


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_in_tmp(tmp_path):
    init_vault(str(tmp_path), PASSWORD)
    save_vault(str(tmp_path), PASSWORD, {"DB_URL": "postgres://localhost", "TOKEN": "xyz"})
    return str(tmp_path)


def _invoke(runner, vault_dir, *args):
    return runner.invoke(
        tag_group,
        [*args, "--password", PASSWORD, "--vault-dir", vault_dir],
        catch_exceptions=False,
    )


def test_add_tag_success(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "add", "DB_URL", "database")
    assert result.exit_code == 0
    assert "added" in result.output


def test_add_tag_unknown_variable_fails(runner, vault_in_tmp):
    result = runner.invoke(
        tag_group,
        ["add", "NO_SUCH_VAR", "mytag", "--password", PASSWORD, "--vault-dir", vault_in_tmp],
    )
    assert result.exit_code != 0
    assert "not found" in result.output


def test_remove_tag_success(runner, vault_in_tmp):
    _invoke(runner, vault_in_tmp, "add", "TOKEN", "secret")
    result = _invoke(runner, vault_in_tmp, "remove", "TOKEN", "secret")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_remove_tag_not_present_fails(runner, vault_in_tmp):
    result = runner.invoke(
        tag_group,
        ["remove", "TOKEN", "ghost", "--password", PASSWORD, "--vault-dir", vault_in_tmp],
    )
    assert result.exit_code != 0


def test_list_tags_empty(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "list")
    assert result.exit_code == 0
    assert "No tags" in result.output


def test_list_tags_shows_entries(runner, vault_in_tmp):
    _invoke(runner, vault_in_tmp, "add", "DB_URL", "infra")
    result = _invoke(runner, vault_in_tmp, "list")
    assert "DB_URL" in result.output
    assert "infra" in result.output


def test_filter_tag_shows_matching(runner, vault_in_tmp):
    _invoke(runner, vault_in_tmp, "add", "DB_URL", "core")
    _invoke(runner, vault_in_tmp, "add", "TOKEN", "core")
    result = _invoke(runner, vault_in_tmp, "filter", "core")
    assert "DB_URL" in result.output
    assert "TOKEN" in result.output


def test_filter_tag_no_results(runner, vault_in_tmp):
    result = _invoke(runner, vault_in_tmp, "filter", "nope")
    assert result.exit_code == 0
    assert "No variables" in result.output
