"""Integration tests for the template CLI commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_template import template_group
from envault.vault import init_vault, save_vault


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def vault_in_tmp(tmp_path):
    """Initialise a vault with a couple of variables and return (vault_dir, password)."""
    password = "s3cr3t"
    init_vault(tmp_path, password)
    save_vault(tmp_path, password, {"APP_HOST": "example.com", "APP_PORT": "8080"})
    return tmp_path, password


def _invoke(runner, vault_dir, args, input_text=None):
    return runner.invoke(template_group, ["--vault-dir", str(vault_dir)] + args, input=input_text, catch_exceptions=False)


def test_render_substitutes_variables(runner, vault_in_tmp, tmp_path):
    vdir, password = vault_in_tmp
    tpl = tmp_path / "app.conf.tpl"
    tpl.write_text("host={{ APP_HOST }}\nport={{ APP_PORT }}\n")
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--password", password, "--vault-dir", str(vdir)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "host=example.com" in result.output
    assert "port=8080" in result.output


def test_render_warns_on_missing_placeholder(runner, vault_in_tmp, tmp_path):
    vdir, password = vault_in_tmp
    tpl = tmp_path / "missing.tpl"
    tpl.write_text("value={{ UNDEFINED_KEY }}")
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--password", password, "--vault-dir", str(vdir)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "UNDEFINED_KEY" in result.output  # warning goes to stderr but CliRunner mixes streams


def test_render_strict_fails_on_missing(runner, vault_in_tmp, tmp_path):
    vdir, password = vault_in_tmp
    tpl = tmp_path / "strict.tpl"
    tpl.write_text("{{ MISSING }}")
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--password", password, "--strict", "--vault-dir", str(vdir)],
    )
    assert result.exit_code != 0
    assert "MISSING" in result.output


def test_render_to_output_file(runner, vault_in_tmp, tmp_path):
    vdir, password = vault_in_tmp
    tpl = tmp_path / "out.tpl"
    tpl.write_text("{{ APP_HOST }}")
    out_file = tmp_path / "rendered.txt"
    result = runner.invoke(
        template_group,
        ["render", str(tpl), "--password", password, "--output", str(out_file), "--vault-dir", str(vdir)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert out_file.read_text() == "example.com"


def test_list_placeholders_cmd(runner, tmp_path):
    tpl = tmp_path / "demo.tpl"
    tpl.write_text("{{ HOST }}:{{ PORT }}/{{ HOST }}")
    result = runner.invoke(template_group, ["list-placeholders", str(tpl)], catch_exceptions=False)
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines == ["HOST", "PORT"]


def test_list_placeholders_no_matches(runner, tmp_path):
    tpl = tmp_path / "plain.txt"
    tpl.write_text("nothing special here")
    result = runner.invoke(template_group, ["list-placeholders", str(tpl)], catch_exceptions=False)
    assert result.exit_code == 0
    assert "No placeholders" in result.output
