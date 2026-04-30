"""CLI commands for template rendering."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from envault.template import TemplateError, list_placeholders, render_template
from envault.vault import load_vault


def _resolve_vault_dir(vault_dir: str | None) -> Path:
    return Path(vault_dir) if vault_dir else Path.cwd()


@click.group("template")
def template_group() -> None:
    """Render templates using vault variables."""


@template_group.command("render")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--output", "-o", default=None, help="Output file (default: stdout).")
@click.option("--strict", is_flag=True, default=False, help="Fail on missing variables.")
@click.option("--vault-dir", default=None, hidden=True)
def render_cmd(template_file: str, password: str, output: str | None, strict: bool, vault_dir: str | None) -> None:
    """Render TEMPLATE_FILE substituting {{ KEY }} placeholders from the vault."""
    vdir = _resolve_vault_dir(vault_dir)
    try:
        variables = load_vault(vdir, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    template_text = Path(template_file).read_text(encoding="utf-8")
    try:
        result = render_template(template_text, variables, strict=strict)
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc

    if result.missing:
        click.echo(f"Warning: {len(result.missing)} placeholder(s) not resolved: {', '.join(result.missing)}", err=True)

    if output:
        Path(output).write_text(result.output, encoding="utf-8")
        click.echo(f"Rendered to {output} ({len(result.resolved)} variable(s) substituted).")
    else:
        click.echo(result.output, nl=False)


@template_group.command("list-placeholders")
@click.argument("template_file", type=click.Path(exists=True, dir_okay=False))
def list_placeholders_cmd(template_file: str) -> None:
    """List all {{ KEY }} placeholders found in TEMPLATE_FILE."""
    template_text = Path(template_file).read_text(encoding="utf-8")
    names = list_placeholders(template_text)
    if not names:
        click.echo("No placeholders found.")
        return
    for name in names:
        click.echo(name)
