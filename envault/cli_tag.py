"""CLI commands for tagging vault variables."""

from __future__ import annotations

import os

import click

from envault.tag import TagError, add_tag, filter_by_tag, list_tags, remove_tag


def _resolve_vault_dir(vault_dir: Optional[str]) -> str:  # noqa: F821
    return vault_dir or os.environ.get("ENVAULT_DIR", ".")


@click.group(name="tag")
def tag_group() -> None:
    """Manage tags on vault variables."""


@tag_group.command("add")
@click.argument("variable")
@click.argument("tag")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, envvar="ENVAULT_DIR")
def add_tag_cmd(variable: str, tag: str, password: str, vault_dir: str) -> None:
    """Add TAG to VARIABLE."""
    vault_dir = _resolve_vault_dir(vault_dir)
    try:
        add_tag(vault_dir, password, variable, tag)
        click.echo(f"Tag '{tag}' added to '{variable}'.")
    except TagError as exc:
        raise click.ClickException(str(exc)) from exc


@tag_group.command("remove")
@click.argument("variable")
@click.argument("tag")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, envvar="ENVAULT_DIR")
def remove_tag_cmd(variable: str, tag: str, password: str, vault_dir: str) -> None:
    """Remove TAG from VARIABLE."""
    vault_dir = _resolve_vault_dir(vault_dir)
    try:
        remove_tag(vault_dir, password, variable, tag)
        click.echo(f"Tag '{tag}' removed from '{variable}'.")
    except TagError as exc:
        raise click.ClickException(str(exc)) from exc


@tag_group.command("list")
@click.option("--variable", default=None, help="Filter to a specific variable.")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, envvar="ENVAULT_DIR")
def list_tags_cmd(variable: str, password: str, vault_dir: str) -> None:
    """List tags, optionally filtered to a single VARIABLE."""
    vault_dir = _resolve_vault_dir(vault_dir)
    tags = list_tags(vault_dir, password, variable)
    if not tags:
        click.echo("No tags found.")
        return
    for var, var_tags in sorted(tags.items()):
        click.echo(f"{var}: {', '.join(sorted(var_tags))}")


@tag_group.command("filter")
@click.argument("tag")
@click.option("--password", envvar="ENVAULT_PASSWORD", prompt=True, hide_input=True)
@click.option("--vault-dir", default=None, envvar="ENVAULT_DIR")
def filter_tag_cmd(tag: str, password: str, vault_dir: str) -> None:
    """Show all variables carrying TAG."""
    vault_dir = _resolve_vault_dir(vault_dir)
    results = filter_by_tag(vault_dir, password, tag)
    if not results:
        click.echo(f"No variables found with tag '{tag}'.")
        return
    for var, value in sorted(results.items()):
        click.echo(f"{var}={value}")
