"""Tests for envault/cli_audit.py"""

import pytest
from click.testing import CliRunner
from pathlib import Path

from envault.cli_audit import audit_group
from envault.audit import record_event, AUDIT_LOG_FILENAME


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_in_tmp(tmp_path):
    """Return a fake vault path inside tmp_path."""
    vault_file = tmp_path / ".envault"
    vault_file.write_text("placeholder")
    return str(vault_file)


def test_log_no_entries(runner, vault_in_tmp):
    result = runner.invoke(audit_group, ["log", "--vault", vault_in_tmp])
    assert result.exit_code == 0
    assert "No audit log entries found" in result.output


def test_log_shows_entries(runner, vault_in_tmp, tmp_path):
    record_event(str(tmp_path), action="set", key="DB_URL", user="alice")
    result = runner.invoke(audit_group, ["log", "--vault", vault_in_tmp])
    assert result.exit_code == 0
    assert "set" in result.output
    assert "alice" in result.output
    assert "DB_URL" in result.output


def test_log_filter_by_action(runner, vault_in_tmp, tmp_path):
    record_event(str(tmp_path), action="set", key="A")
    record_event(str(tmp_path), action="get", key="B")
    result = runner.invoke(
        audit_group, ["log", "--vault", vault_in_tmp, "--action", "get"]
    )
    assert result.exit_code == 0
    assert "get" in result.output
    # 'set' action should not appear as action label in filtered output
    lines = [l for l in result.output.splitlines() if l.strip()]
    assert all("get" in line for line in lines)


def test_log_tail_limits_output(runner, vault_in_tmp, tmp_path):
    for i in range(5):
        record_event(str(tmp_path), action="set", key=f"VAR_{i}")
    result = runner.invoke(
        audit_group, ["log", "--vault", vault_in_tmp, "--tail", "2"]
    )
    assert result.exit_code == 0
    lines = [l for l in result.output.splitlines() if l.strip()]
    assert len(lines) == 2


def test_clear_audit_log(runner, vault_in_tmp, tmp_path):
    record_event(str(tmp_path), action="init")
    log_path = tmp_path / AUDIT_LOG_FILENAME
    assert log_path.exists()
    result = runner.invoke(
        audit_group, ["clear", "--vault", vault_in_tmp], input="y\n"
    )
    assert result.exit_code == 0
    assert "cleared" in result.output
    assert not log_path.exists()


def test_clear_audit_log_aborted(runner, vault_in_tmp, tmp_path):
    record_event(str(tmp_path), action="init")
    log_path = tmp_path / AUDIT_LOG_FILENAME
    result = runner.invoke(
        audit_group, ["clear", "--vault", vault_in_tmp], input="n\n"
    )
    assert result.exit_code != 0 or "Aborted" in result.output
    assert log_path.exists()
